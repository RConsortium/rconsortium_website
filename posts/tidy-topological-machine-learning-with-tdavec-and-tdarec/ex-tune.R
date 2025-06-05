library(tidymodels)
set.seed(0)
dat <- subset(mtcars, select = c(mpg, cyl, hp, wt))
folds <- vfold_cv(dat, v = 3L)

# recipe with no hyperparameters
rec <- recipe(mpg ~ ., data = dat)

# model with a hyperparameter not requiring finalization
spec <- rand_forest(trees = 5, min_n = tune()) |> 
  set_mode("regression") |> 
  set_engine("randomForest")

# tune over a grid
res_g <- tune_grid(
  spec,
  preprocessor = rec,
  resamples = folds
)
collect_metrics(res_g) |> head()
# tune using bayesian optimization
res <- tune_bayes(
  spec,
  preprocessor = rec,
  resamples = folds,
  iter = 2, initial = 6
)
collect_metrics(res) |> head()

# random forest model, still with a hyperparameter requiring finalization
spec_t <- rand_forest(trees = 5, min_n = tune(), mtry = tune()) |> 
  set_mode("regression") |> 
  set_engine("randomForest")
(mtry_param <- finalize(mtry(), subset(dat, select = c(-mpg))))

# Answer 1: Extract and update the dials from the model specification.

res_g <- tune_grid(
  spec_t,
  preprocessor = rec,
  resamples = folds,
  grid = grid_regular(mtry_param, min_n(), levels = 3)
)
collect_metrics(res_g) |> head()

rf_param <- spec_t |> 
  extract_parameter_set_dials() |> 
  update(mtry = mtry_param)
res <- tune_bayes(
  spec_t,
  preprocessor = rec,
  resamples = folds,
  param_info = rf_param,
  iter = 2, initial = 6
)
collect_metrics(res) |> head()

# Answer 1b: Extract and update the dials from a prepared workflow.

wflow <- workflow() |> 
  add_recipe(rec) |> 
  add_model(spec_t)

res_g <- tune_grid(
  wflow,
  resamples = folds,
  grid = grid_regular(mtry_param, min_n(), levels = 3)
)
collect_metrics(res_g) |> head()

wf_param <- wflow |> 
  extract_parameter_set_dials() |> 
  update(mtry = mtry_param)
res <- tune_bayes(
  wflow,
  resamples = folds,
  param_info = wf_param,
  iter = 2, initial = 6
)
collect_metrics(res) |> head()

# also tune a preprocessing hyperparameter
rec_pca <- recipe(mpg ~ ., data = dat) |> 
  step_pca(num_comp = tune())

(num_comp_param <- finalize(num_comp(), subset(dat, select = c(-mpg))))

# Answer 2a

rf_pca_grid <- merge(
  grid_regular(num_comp_param, levels = 3),
  grid_regular(mtry_param, min_n(), levels = 3)
)
res_g <- tune_grid(
  spec_t,
  preprocessor = rec_pca,
  resamples = folds,
  grid = rf_pca_grid
)
collect_metrics(res_g) |> head()

rf_pca_param <- bind_rows(
  extract_parameter_set_dials(rec_pca),
  extract_parameter_set_dials(spec_t)
) |> 
  update(mtry = mtry_param, num_comp = num_comp_param)
res <- tune_bayes(
  spec_t,
  preprocessor = rec_pca,
  resamples = folds,
  param_info = rf_pca_param,
  iter = 2, initial = 6
)
collect_metrics(res) |> head()

# Answer 2b

wflow <- workflow() |> 
  add_recipe(rec_pca) |> 
  add_model(spec_t)

grid_wf <- merge(
  grid_regular(num_comp_param, levels = 3),
  grid_regular(mtry_param, min_n(), levels = 3)
)
res_g <- tune_grid(
  wflow,
  resamples = folds,
  grid = grid_wf
)
collect_metrics(res_g) |> head()

rf_pca_wf_param <- wflow |> 
  extract_parameter_set_dials() |> 
  update(mtry = mtry_param, num_comp = num_comp_param)
res <- tune_bayes(
  wflow,
  resamples = folds,
  param_info = rf_pca_wf_param,
  iter = 2, initial = 6
)
collect_metrics(res) |> head()
