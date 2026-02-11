import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.ticker import FuncFormatter
from scipy.stats import mannwhitneyu
from matplotlib.ticker import FormatStrFormatter

# Specify the path to your Excel file
file_path = "/Users/fg221/OneDrive - Imperial College London/PhD Milestone/PhD thesis/PhD thesis_Feng Gao/Engineering a Brighter Bacterial Bioluminescence Pathway/dna5298&dna3132_comparison.xlsx"

# Read the sheet named "data_to_code"
df = pd.read_excel(file_path, sheet_name="data_to_code")

# Quick check
#print(df.head())

# Melt to long format so each row is one measurement
df_long = df.melt(
    id_vars="Time, h",
    value_vars=[col for col in df.columns if col != "Time, h"],
    var_name="construct",
    value_name="lum"
)

# Derive base group name and replicate index
#    – base: drop “.N” suffix
#    – replicate: the suffix number + 1, or 1 if no suffix
df_long["base"] = df_long["construct"].str.replace(r"\.\d+$", "", regex=True)
suffix = df_long["construct"].str.extract(r"\.(\d+)$")[0]
df_long["replicate"] = suffix.fillna(0).astype(int) + 1

# Compute AUC per base + replicate using trapezoidal rule
auc_df = (
    df_long
    .groupby(["base", "replicate"], sort=False)
    .apply(lambda grp: np.trapz(grp["lum"], grp["Time, h"]))
    .reset_index(name="AUC")
)

# Inspect the result
#print(auc_df)


fig, ax = plt.subplots(figsize=(2.2, 2.2), facecolor='none')

# Draw boxplot (black edges, no fill)
ax = sns.boxplot (
    data=auc_df, x="base", y="AUC", ax=ax,
    showcaps=True,
    linewidth=0.3,            # make whole box edge thinner
    zorder=4,                 # draw above the grid
    boxprops=dict(facecolor="none", edgecolor="white", linewidth=1),
    whiskerprops=dict(color="white", linewidth=0.3),
    capprops=dict(color="white", linewidth=0.3),
    medianprops=dict(color="white", linewidth=0.5),
    flierprops=dict(marker="o", markerfacecolor="white", markeredgecolor="none", markersize=5)
)

# Define your colors for each group
palette_map = {
    "dna3132": "#cb9e59",
    "dna5298": "#ebe05e",
}

# Overlay individual points (white)
sns.stripplot(
    data=auc_df,
    x="base", y="AUC",
    jitter=True,
    size=3,
    palette=palette_map,
    edgecolor="none",
    alpha=0.8,
    zorder=6
)

# Transparent axes & background
ax.set_facecolor('none')
plt.gca().patch.set_alpha(0)

# Keep grid
#ax.grid(True, color="white", linestyle="--", linewidth=0.5, alpha=0.3)
ax.grid(False)

# Hide only the top and right spines
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Style the left and bottom spines (axes lines)
ax.spines["left"].set_color("white")
ax.spines["bottom"].set_color("white")


# Logarithmic Y-axis with compact tick labels (numbers only) 
# and a single ×10^8 scale indicator at the top
ax.set_yscale("log")

# Do NOT set ylim here — the final y-limits will be determined later
# based on the data, and tick positions will be adjusted afterward.
# Here we only define the tick label formatter:
# divide the actual values by 1e8 so that only the numeric part
# (e.g. 2.4, 2.6, 3.0) is shown on the axis.
ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y/1e8:.1f}"))

# Disable any automatic scientific-notation offset text
# to avoid redundant or oversized 10^n labels
ax.yaxis.offsetText.set_visible(False)

# For small figures, disable minor ticks for a cleaner appearance
ax.minorticks_off()


# Tick styling (white)
ax.tick_params(axis="y", which="major", length=2, width=0.5, colors="white", labelsize=8)
ax.tick_params(axis="y", which="minor", length=2, width=0.5, colors="white")
ax.tick_params(axis="x", which="major", length=2, width=0.5, colors="white", labelsize=8)

# font and size for y tick labels
for label in ax.get_yticklabels():
    label.set_fontfamily("Helvetica")
    label.set_fontsize(8)
    label.set_color("white")

# font and size for x tick labels (match y ticks)
for label in ax.get_xticklabels():
    label.set_fontfamily("Helvetica")
    label.set_fontsize(8)
    label.set_color("white")

# Offset text styling
ax.yaxis.get_offset_text().set_fontfamily("Helvetica")
ax.yaxis.get_offset_text().set_fontsize(8)
ax.yaxis.get_offset_text().set_color("white")

# Make the left and bottom spines thinner
ax.spines['left'].set_linewidth(0.5)
ax.spines['bottom'].set_linewidth(0.5)

# Add a small margin around the data so axes don’t hug the corner
ax.margins(x=0.05, y=0.05)

# Move the bottom and left spines outward to create a visible gap
ax.spines['left'].set_position(('outward', 10))    # 10 points to the left
ax.spines['bottom'].set_position(('outward', 10))  # 10 points downward

# Labels in white
#ax.set_ylabel("AUC (RLU·h)", color="white", fontsize=8, fontfamily="Helvetica")
ax.set_ylabel(
    r"log$_{10}$(luminescence/OD$_{600}$, AUC)",
    color="white",
    fontsize=8,
    fontfamily="Helvetica",
    fontweight="normal"
)

ax.set_xlabel("", color="white", fontsize=8, fontfamily="Helvetica")

# Auto‐limit to your data (with a little padding)
ymin = auc_df["AUC"].min() * 0.9
ymax = auc_df["AUC"].max() * 1.1
ax.set_ylim(ymin, ymax)

# ---- AFTER setting ylim: select clean, human-friendly tick positions
#      and add a single ×10^8 scale indicator ----
# Generate visually pleasing tick values within [ymin, ymax],
# such as 2.4, 2.6, 2.8, 3.0, etc., using a step size of 0.2
lo = np.ceil((ymin / 1e8) * 5) / 5    # step size = 0.2
hi = np.floor((ymax / 1e8) * 5) / 5
tick_vals = np.arange(lo, hi + 0.0001, 0.2)

# If the data range is too narrow and results in too few ticks,
# fall back to three representative ticks: bottom, middle, and top.
# For a logarithmic axis, the midpoint is best represented
# by the geometric mean.
if len(tick_vals) < 2:
    mid = (ymin * ymax) ** 0.5
    tick_vals = np.array([ymin / 1e8, mid / 1e8, ymax / 1e8])

# Apply the tick positions (convert back to absolute values)
ax.set_yticks(tick_vals * 1e8)

# Add a single ×10^8 label at the top-left of the y-axis
ax.text(
    -0.12, 1.02,
    r"$\times 10^8$",
    transform=ax.transAxes,
    ha="left", va="bottom",
    fontsize=8,
    color="white",
    fontfamily="Helvetica"
)

# Annotate sample size under each box
#group_counts = auc_df["base"].value_counts().loc[auc_df["base"].unique()]
#for i, group in enumerate(auc_df["base"].unique()):
#    ax.text(
#        i, 0.01, f"N = {group_counts[group]}",
#        ha="center", va="top",
#        color="white", fontsize=12,
#        transform=ax.get_xaxis_transform()
#    )

# assume auc_df exists with columns base, replicate, AUC
group1, group2 = auc_df['base'].unique()
data1 = auc_df.loc[auc_df['base']==group1, 'AUC']
data2 = auc_df.loc[auc_df['base']==group2, 'AUC']

# geometric‐mean fold‐change
gm1 = np.exp(np.mean(np.log(data1)))
gm2 = np.exp(np.mean(np.log(data2)))
fold_change = gm2 / gm1

# mannwhitney test on log10(AUC)
p_value = mannwhitneyu(np.log10(data2), np.log10(data1), alternative='two-sided').pvalue

# Compute bar height just above your data
ymin = auc_df["AUC"].min()
bar_y = ymin * 0.98          # 5% above the highest point
cap_height = ymin * 0.01     # 2% of bar_y for the little caps

# Draw a single comparison bar between the two groups (at x=0 and x=1)
x1, x2 = 0, 1

# horizontal line
ax.hlines(bar_y, x1, x2, color="white", linewidth=0.5, zorder=10)

# vertical end‐caps
ax.vlines([x1, x2], [bar_y, bar_y], [bar_y + cap_height, bar_y + cap_height],
          color="white", linewidth=0.5, zorder=10)


# Annotate fold‐change and p‐value just below the bar
annotation = rf"{fold_change:.1f}-fold, $p$ = {p_value:.1e}"
ax.text(
    (x1 + x2) / 2,
    bar_y - cap_height * 1.5,
    annotation,
    ha="center", va="top",
    color="white", fontsize=8, fontfamily="Helvetica",
    zorder=11
)

#ax.set_title(
#    "Brightness Comparison",
#    color="white",
#    fontsize=16,
#    pad=15  # space between title and plot
#)

# Save as transparent SVG
desktop = Path.home() / 'Desktop'
fig_path_svg = desktop / 'Bio_AUC_compare.svg'
plt.tight_layout()
plt.savefig(fig_path_svg, format="svg", transparent=True)
plt.show()

print("Saved figure to", fig_path_svg)

