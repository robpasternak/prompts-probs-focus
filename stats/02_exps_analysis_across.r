#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  packages <- c(
    "readr",
    "dplyr",
    "tibble",
    "purrr",
    "lme4",
    "lmerTest"
  )

  missing <- packages[
    !vapply(
      packages,
      requireNamespace,
      logical(1),
      quietly = TRUE
    )
  ]

  if (length(missing)) {
    stop(
      "Missing package(s): ",
      paste(missing, collapse = ", "),
      ". Install with: install.packages(c(",
      paste(sprintf("'%s'", missing), collapse = ", "),
      "))",
      call. = FALSE
    )
  }

  library(readr)
  library(dplyr)
  library(tibble)
  library(purrr)
  library(lme4)
  library(lmerTest)
})

args <- commandArgs(trailingOnly = TRUE)

exp01_file <- if (length(args) >= 1) {
  args[[1]]
} else {
  "stats/exp_01_results.csv"
}

exp02_file <- if (length(args) >= 2) {
  args[[2]]
} else {
  "stats/exp_02_results.csv"
}

out_dir <- if (length(args) >= 3) {
  args[[3]]
} else {
  "."
}

dir.create(
  out_dir,
  recursive = TRUE,
  showWarnings = FALSE
)

required_columns <- c(
  "original_data_index",
  "correct",
  "data_type",
  "condition",
  "fm_type",
  "model"
)


# -------------------------------------------------------------------------
# Convert correctness column to 0/1
# -------------------------------------------------------------------------

coerce_correct <- function(correct_col, path) {

  correct <- dplyr::case_when(
    tolower(trimws(as.character(correct_col))) %in%
      c("true", "t", "1", "yes") ~ 1,

    tolower(trimws(as.character(correct_col))) %in%
      c("false", "f", "0", "no") ~ 0,

    is.na(tolower(trimws(as.character(correct_col)))) ~ NA_real_,

    TRUE ~ NA_real_
  )

  if (any(is.na(correct) & !is.na(correct_col))) {
    stop(
      "Unrecognized value(s) in 'correct' in ",
      path,
      call. = FALSE
    )
  }

  correct
}


# -------------------------------------------------------------------------
# Read one experiment
# -------------------------------------------------------------------------

read_experiment <- function(path, expected_fm_type) {

  dat <- readr::read_csv(
    path,
    show_col_types = FALSE
  )

  missing <- setdiff(
    required_columns,
    names(dat)
  )

  if (length(missing)) {
    stop(
      path,
      " is missing required column(s): ",
      paste(missing, collapse = ", "),
      call. = FALSE
    )
  }

  dat <- dat %>%
    mutate(
      correct = coerce_correct(
        .data$correct,
        path
      ),

      original_data_index =
        as.character(.data$original_data_index),

      data_type =
        as.character(.data$data_type),

      condition =
        trimws(as.character(.data$condition)),

      fm_type =
        as.character(.data$fm_type),

      model =
        as.character(.data$model)
    ) %>%
    filter(
      .data$condition == "Target"
    )

  actual_fm <- sort(
    unique(
      na.omit(dat$fm_type)
    )
  )

  expected_fm <- sort(
    unique(expected_fm_type)
  )

  if (!identical(actual_fm, expected_fm)) {
    stop(
      path,
      " has unexpected fm_type value(s): ",
      paste(actual_fm, collapse = ", "),
      ". Expected: ",
      paste(expected_fm_type, collapse = ", "),
      call. = FALSE
    )
  }

  dat
}


# -------------------------------------------------------------------------
# Average accuracy across focus markers
# -------------------------------------------------------------------------

average_accuracy_by_item_type <- function(dat) {

  dat %>%
    filter(
      !is.na(.data$correct),
      !is.na(.data$original_data_index),
      !is.na(.data$data_type),
      !is.na(.data$model)
    ) %>%
    group_by(
      .data$model,
      .data$original_data_index,
      .data$data_type
    ) %>%
    summarize(
      avg_accuracy = mean(.data$correct),
      n_obs = n(),
      .groups = "drop"
    )
}


# -------------------------------------------------------------------------
# Build paired Standard / Random dataset
# -------------------------------------------------------------------------

build_baseline_dataframe <- function(exp01, exp02) {

  exp01_avg <- average_accuracy_by_item_type(
    exp01
  )

  exp02_avg <- average_accuracy_by_item_type(
    exp02
  )

  # Check that every model × item × method combination
  # exists in both experiments.

  only_exp01 <- anti_join(
    exp01_avg,
    exp02_avg,
    by = c(
      "model",
      "original_data_index",
      "data_type"
    )
  )

  only_exp02 <- anti_join(
    exp02_avg,
    exp01_avg,
    by = c(
      "model",
      "original_data_index",
      "data_type"
    )
  )

  if (
    nrow(only_exp01) > 0 ||
    nrow(only_exp02) > 0
  ) {

    stop(
      "Unmatched model + original_data_index + data_type ",
      "combinations between experiments.\n",
      "In exp_01 only: ",
      nrow(only_exp01),
      "\n",
      "In exp_02 only: ",
      nrow(only_exp02),
      call. = FALSE
    )
  }

  joined <- inner_join(
    exp01_avg,
    exp02_avg,
    by = c(
      "model",
      "original_data_index",
      "data_type"
    ),
    suffix = c(
      "_exp01",
      "_exp02"
    )
  )

  joined %>%
    transmute(
      model =
        .data$model,

      original_data_index =
        factor(.data$original_data_index),

      data_type =
        .data$data_type,

      standard_accuracy =
        .data$avg_accuracy_exp01,

      random_accuracy =
        .data$avg_accuracy_exp02,

      n_standard =
        .data$n_obs_exp01,

      n_random =
        .data$n_obs_exp02
    ) %>%
    arrange(
      .data$model,
      .data$original_data_index,
      .data$data_type
    )
}


# -------------------------------------------------------------------------
# Fit model
# -------------------------------------------------------------------------

fit_baseline_model <- function(df) {

  lmerTest::lmer(
    random_accuracy ~
      standard_accuracy + data_type +
      (1 | original_data_index) +
      (1 | model),

    data = df,

    REML = FALSE,

    control = lmerControl(
      optimizer = "bobyqa",
      optCtrl = list(
        maxfun = 2e5
      )
    )
  )
}


# -------------------------------------------------------------------------
# Extract fixed effects
# -------------------------------------------------------------------------

extract_fixed_effects <- function(
  fit,
  model_name,
  n_rows
) {

  coef_df <- as.data.frame(
    summary(fit)$coefficients
  )

  coef_df$term <- rownames(coef_df)
  rownames(coef_df) <- NULL

  has_df <- "df" %in% names(coef_df)
  has_p <- "Pr(>|t|)" %in% names(coef_df)

  as_tibble(coef_df) %>%
    mutate(
      estimate =
        .data[["Estimate"]],

      std_error =
        .data[["Std. Error"]],

      df =
        if (has_df) {
          .data[["df"]]
        } else {
          NA_real_
        },

      statistic =
        .data[["t value"]],

      p_value =
        if (has_p) {
          .data[["Pr(>|t|)"]]
        } else {
          NA_real_
        },

      analysis =
        "baseline_adjusted_random_accuracy_centered",

      model =
        model_name,

      n_rows =
        n_rows,

      conf_low =
        .data$estimate -
        1.96 * .data$std_error,

      conf_high =
        .data$estimate +
        1.96 * .data$std_error,

      singular_fit =
        isSingular(
          fit,
          tol = 1e-4
        ),

      converged =
        is.null(
          fit@optinfo$conv$lme4$messages
        ),

      optimizer =
        fit@optinfo$optimizer,

      .before = 1
    ) %>%
    select(
      all_of(
        c(
          "analysis",
          "model",
          "term",
          "estimate",
          "std_error",
          "df",
          "statistic",
          "p_value",
          "conf_low",
          "conf_high",
          "n_rows",
          "singular_fit",
          "converged",
          "optimizer"
        )
      )
    )
}


# -------------------------------------------------------------------------
# Fit one pooled model across all underlying LLMs
# -------------------------------------------------------------------------

run_baseline_model <- function(df) {

  md <- df %>%
    mutate(
      data_type =
        if (
          "string_probs" %in% .data$data_type
        ) {

          relevel(
            factor(.data$data_type),
            ref = "string_probs"
          )

        } else {

          factor(.data$data_type)

        },

      model =
        factor(.data$model)
    )

  fit <- fit_baseline_model(
    md
  )

  extract_fixed_effects(
    fit,
    "all_models",
    nrow(md)
  )
}


# -------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------

message(
  "Reading ",
  exp01_file
)

exp01 <- read_experiment(
  exp01_file,
  "Standard"
)


message(
  "Reading ",
  exp02_file
)

exp02 <- read_experiment(
  exp02_file,
  "Ad Hoc"
)


message(
  "Computing per-item + method average accuracies..."
)

baseline_df <- build_baseline_dataframe(
  exp01,
  exp02
)


message(
  "Fitting baseline-adjusted mixed-effects model..."
)

model_stats <- run_baseline_model(
  baseline_df
)


# -------------------------------------------------------------------------
# Save results
# -------------------------------------------------------------------------

out_file <- file.path(
  out_dir,
  "stats/stats_exps_across.csv"
)

dir.create(
  dirname(out_file),
  recursive = TRUE,
  showWarnings = FALSE
)

readr::write_csv(
  model_stats,
  out_file
)

message(
  "Finished successfully."
)

message(
  "Model output written to: ",
  normalizePath(
    out_file,
    mustWork = FALSE
  )
)

message(
  "Model fixed effects summary:"
)

print(model_stats)