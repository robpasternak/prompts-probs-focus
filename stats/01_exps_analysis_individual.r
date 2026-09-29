# Install packages if needed
# install.packages("lme4")
# install.packages("emmeans")
# install.packages("tidyverse")

library(lme4)
library(emmeans)
library(tidyverse)


# Import data
data_1 <- read.csv(
  "stats/exp_01_results.csv",
  stringsAsFactors = FALSE
)

data_2 <- read.csv(
  "stats/exp_02_results.csv",
  stringsAsFactors = FALSE
)

# Restrict analysis to Target condition only
data_1 <- data_1 %>%
  filter(.data$condition == "Target")
data_2 <- data_2 %>%
  filter(.data$condition == "Target")


# Convert variable types
data_1$item <- factor(data_1$original_data_index)
data_2$item <- factor(data_2$original_data_index)

# Method should be categorical
data_1$method <- factor(
  levels = c("string_probs", "forced_choice_1", "forced_choice_2", "yes_no_1", "yes_no_2"),
  data_1$data_type
)
data_2$method <- factor(
  levels = c("string_probs", "forced_choice_1", "forced_choice_2", "yes_no_1", "yes_no_2"),
  data_2$data_type
)

# Model should be categorical
data_1$model <- factor(data_1$model)
data_2$model <- factor(data_2$model)


# Focus marker should be categorical (used as a random effect)
data_1$focus_marker <- factor(data_1$focus_marker)
data_2$focus_marker <- factor(data_2$focus_marker)

# Correct should be numeric 0/1
data_1$correct <- case_when(
  tolower(as.character(data_1$correct)) %in% c("true", "1", "yes") ~ 1,
  tolower(as.character(data_1$correct)) %in% c("false", "0", "no") ~ 0,
  TRUE ~ NA_real_
)
data_2$correct <- case_when(
  tolower(as.character(data_2$correct)) %in% c("true", "1", "yes") ~ 1,
  tolower(as.character(data_2$correct)) %in% c("false", "0", "no") ~ 0,
  TRUE ~ NA_real_
)


# Function for fitting mixed-effect logistic regression
fit_model_for_model <- function(model_name, model_data) {
  message("Running mixed model for model: ", model_name)

  fit <- glmer(
    correct ~ method + (1 | focus_marker) + (1 | item),
    family = binomial,
    data = model_data,
    control = glmerControl(
      optimizer = "bobyqa"
    )
  )

  coef_table <- summary(fit)$coefficients

  results <- data.frame(
    term = rownames(coef_table),
    estimate = coef_table[, 1],
    standard_error = coef_table[, 2],
    z_value = coef_table[, 3],
    p_value = coef_table[, 4],
    odds_ratio = exp(coef_table[, 1])
  )

  results$model <- model_name

  results
}

unique_models_1 <- unique(as.character(data_1$model))
unique_models_2 <- unique(as.character(data_2$model))

# Stats for dataset 1
all_stats_1 <- lapply(unique_models_1, function(model_name) {
  model_data_1 <- data_1 %>%
    filter(.data$model == model_name)
  fit_model_for_model(model_name, model_data_1)
}) %>%
  bind_rows() %>%
  select(model, everything())

write.csv(
  all_stats_1,
  "stats/stats_exp_01.csv",
  row.names = FALSE
)

# Stats for dataset 2
all_stats_2 <- lapply(unique_models_2, function(model_name) {
  model_data_2 <- data_2 %>%
    filter(.data$model == model_name)
  fit_model_for_model(model_name, model_data_2)
}) %>%
  bind_rows() %>%
  select(model, everything())

write.csv(
  all_stats_2,
  "stats/stats_exp_02.csv",
  row.names = FALSE
)
