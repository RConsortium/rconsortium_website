library(inphr)
library(ggtda)

prox <- 1

# trefoil1

trefoils1_plts <- purrr::map(trefoils1[1:5], \(.x) {
  pd <- as_tibble(.x)
  pd$dimension <- factor(pd$dimension, levels = 0:2)
  max_prox <- max(pd$death)
  pd |>
    ggplot() +
    coord_fixed() +
    stat_persistence(
      aes(
        start = birth,
        end = death,
        colour = dimension,
        shape = dimension
      ),
      show.legend = TRUE
    ) +
    geom_abline(slope = 1) +
    labs(x = "Birth", y = "Death", color = "Dimension", shape = "Dimension") +
    lims(x = c(0, max_prox), y = c(0, max_prox)) +
    # geom_fundamental_box(
    #   t = prox,
    #   fill = "darkgoldenrod",
    #   color = "transparent"
    # ) +
    scale_color_discrete(drop = FALSE) +
    scale_linetype_discrete(drop = FALSE) +
    scale_shape_discrete(drop = FALSE) +
    theme_persist()
})

# trefoils2

trefoils2_plts <- purrr::map(trefoils2[1:5], \(.x) {
  pd <- as_tibble(.x)
  pd$dimension <- factor(pd$dimension, levels = 0:2)
  max_prox <- max(pd$death)
  pd |>
    ggplot() +
    coord_fixed() +
    stat_persistence(
      aes(
        start = birth,
        end = death,
        colour = dimension,
        shape = dimension
      ),
      show.legend = TRUE
    ) +
    geom_abline(slope = 1) +
    labs(x = "Birth", y = "Death", color = "Dimension", shape = "Dimension") +
    lims(x = c(0, max_prox), y = c(0, max_prox)) +
    # geom_fundamental_box(
    #   t = prox,
    #   fill = "darkgoldenrod",
    #   color = "transparent"
    # ) +
    scale_color_discrete(drop = FALSE) +
    scale_linetype_discrete(drop = FALSE) +
    scale_shape_discrete(drop = FALSE) +
    theme_persist()
})

# archspirals

archspirals_plts <- purrr::map(archspirals[1:5], \(.x) {
  pd <- as_tibble(.x)
  pd$dimension <- factor(pd$dimension, levels = 0:2)
  max_prox <- max(pd$death)
  pd |>
    ggplot() +
    coord_fixed() +
    stat_persistence(
      aes(
        start = birth,
        end = death,
        colour = dimension,
        shape = dimension
      ),
      show.legend = TRUE
    ) +
    geom_abline(slope = 1) +
    labs(x = "Birth", y = "Death", color = "Dimension", shape = "Dimension") +
    lims(x = c(0, max_prox), y = c(0, max_prox)) +
    # geom_fundamental_box(
    #   t = prox,
    #   fill = "darkgoldenrod",
    #   color = "transparent"
    # ) +
    scale_color_discrete(drop = FALSE) +
    scale_linetype_discrete(drop = FALSE) +
    scale_shape_discrete(drop = FALSE) +
    theme_persist()
})

row_label_1 <- patchwork::wrap_elements(
  panel = grid::textGrob('Trefoils 1', rot = 270)
)
row_label_2 <- patchwork::wrap_elements(
  panel = grid::textGrob('Trefoils 2', rot = 270)
)
row_label_3 <- patchwork::wrap_elements(
  panel = grid::textGrob('Archspirals', rot = 270)
)

patchwork::wrap_plots(
  c(
    c(trefoils1_plts, list(row_label_1)),
    c(trefoils2_plts, list(row_label_2)),
    c(archspirals_plts, list(row_label_3))
  ),
  nrow = 3L
) +
  patchwork::plot_layout(guides = "collect", widths = c(rep(1, 5), 0.1)) &
  theme(legend.position = "bottom")

lims <- TDAvec::computeLimits(
  c(
    purrr::map(trefoils1, as.matrix),
    purrr::map(trefoils2, as.matrix),
    purrr::map(archspirals, as.matrix)
  ),
  homDim = 0
)
x <- seq(min(lims), max(lims), len = 1e3)
x <- seq(0, 2.5, len = 1e3)

trefoils1_betti <- purrr::map(trefoils1, \(D) {
  D |>
    as.matrix() |>
    TDAvec::computeBettiCurve(homDim = 0, scaleSeq = x)
}) |>
  do.call(cbind, args = _)

trefoils2_betti <- purrr::map(trefoils2, \(D) {
  D |>
    as.matrix() |>
    TDAvec::computeBettiCurve(homDim = 0, scaleSeq = x)
}) |>
  do.call(cbind, args = _)

archspirals_betti <- purrr::map(archspirals, \(D) {
  D |>
    as.matrix() |>
    TDAvec::computeBettiCurve(homDim = 0, scaleSeq = x)
}) |>
  do.call(cbind, args = _)

n <- 24L
colnames(trefoils1_betti) <- paste0("Trefoils1_", 1:n)
colnames(trefoils2_betti) <- paste0("Trefoils2_", 1:n)
colnames(archspirals_betti) <- paste0("Archspirals_", 1:n)

dplyr::bind_cols(
  r = seq(0, 1, length.out = length(x) - 1),
  trefoils1_betti,
  trefoils2_betti,
  archspirals_betti
) |>
  tidyr::pivot_longer(-r) |>
  tidyr::separate(name, into = c("SampleId", "PointId")) |>
  ggplot2::ggplot(aes(
    x = r,
    y = value,
    color = SampleId,
    group = interaction(SampleId, PointId)
  )) +
  ggplot2::geom_line() +
  labs(x = "Normalized Scale", y = "Betti Curve", color = "Sample") +
  ggplot2::theme_bw() +
  theme(legend.position = "bottom")

out1 <- two_sample_functional_test(
  trefoils1,
  trefoils2,
  dimension = 0,
  representation = "betti"
)
saveRDS(out1, "sandbox/out1.rds")

out2 <- two_sample_functional_test(
  trefoils1,
  archspirals,
  dimension = 0,
  representation = "betti"
)
saveRDS(out2, "sandbox/out2.rds")
