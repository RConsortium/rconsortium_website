# prepare a Tidymodels session and attach {tdarec}
library(tidyverse)
library(tidymodels)
library(tdarec)

# load and partition MNIST training and testing data
data(mnist)
mnist_folds <- vfold_cv(mnist_train, v = 6L)

# specify a pre-processing recipe
scale_seq <- seq(0, 3, by = .05)
recipe(label ~ digit, data = mnist_train) |> 
  step_pd_raster(
    digit, max_hom_degree = tune("ph_degree"),
    keep_original_cols = FALSE
  ) |> 
  step_vpd_pl(
    sample_pd, hom_degree = tune("pl_degree"), xseq = scale_seq, k = 1L,
    keep_original_cols = FALSE
  ) |> 
  print() -> mnist_rec

# specify a classification model
rand_forest(mtry = tune(), trees = tune(), min_n = tune()) |> 
  set_mode("classification") |> 
  set_engine("randomForest") |> 
  print() -> mnist_rf

# generate a hyperparameter tuning grid
mnist_rec_grid <- grid_regular(
  extract_parameter_set_dials(mnist_rec), levels = 2
)
mnist_rf_grid <- grid_regular(
  extract_parameter_set_dials(mnist_rf), levels = 5
)
mnist_grid <- merge(mnist_rec_grid, mnist_rf_grid)

# optimize the model performance
mnist_res <- tune_grid(
  mnist_rf,
  preprocessor = mnist_rec,
  resamples = mnist_folds,
  grid = mnist_grid,
  metrics = metric_set(accuracy)
)
mnist_res |> 
  collect_metrics()
mnist_res |> 
  select_best(metric = "accuracy")
