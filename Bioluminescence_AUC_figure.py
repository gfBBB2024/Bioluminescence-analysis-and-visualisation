import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.ticker import FuncFormatter
from scipy.stats import ttest_ind
from matplotlib.ticker import FormatStrFormatter

# 1) Specify the path to your Excel file
file_path = "/Users/fg221/OneDrive - Imperial College London/PhD Milestone/PhD thesis/PhD thesis_Feng Gao/Engineering a Brighter Bacterial Bioluminescence Pathway/exp_ilux2 and gly5315 test in BY-2/dna5861[ilux2]_dna5298_comparison_in_BY-2/dna5861_dna5298_comparison.xlsx"

# 2) Read the sheet named "data_to_code"
df = pd.read_excel(file_path, sheet_name="data_to_code")

# 3) Quick check
#print(df.head())

# 1) Melt to long format so each row is one measurement
df_long = df.melt(
    id_vars="Time, h",
    value_vars=[col for col in df.columns if col != "Time, h"],
    var_name="construct",
    value_name="lum"
)

# 2) Derive base group name and replicate index
#    – base: drop “.N” suffix
#    – replicate: the suffix number + 1, or 1 if no suffix
df_long["base"] = df_long["construct"].str.replace(r"\.\d+$", "", regex=True)
suffix = df_long["construct"].str.extract(r"\.(\d+)$")[0]
df_long["replicate"] = suffix.fillna(0).astype(int) + 1

# 3) Compute AUC per base + replicate using trapezoidal rule
auc_df = (
    df_long
    .groupby(["base", "replicate"], sort=False)
    .apply(lambda grp: np.trapz(grp["lum"], grp["Time, h"]))
    .reset_index(name="AUC")
)

# 4) Inspect the result
#print(auc_df)


fig, ax = plt.subplots(figsize=(6, 6), facecolor='none')

# 2) Draw boxplot (black edges, no fill)
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
    "dna5861[ilux2]": "#cb9e59",
    "dna5298": "#ebe05e",
}

# 3) Overlay individual points (white)
sns.stripplot(
    data=auc_df,
    x="base", y="AUC",
    jitter=True,
    size=6,
    palette=palette_map,
    edgecolor="none",
    alpha=0.8,
    zorder=6
)

# 4) Transparent axes & background
ax.set_facecolor('none')
plt.gca().patch.set_alpha(0)

# 2) Keep grid
ax.grid(True, color="white", linestyle="--", linewidth=0.5, alpha=0.3)

# 3) Hide only the top and right spines
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# 4) Style the left and bottom spines (axes lines)
ax.spines["left"].set_color("white")
ax.spines["bottom"].set_color("white")


# 5) Logarithmic Y-axis + tick positions/labels
ax.set_yscale("log")
ax.set_ylim(1e6, 5e7)

yticks = [1e6, 1e7, 5e7]
ax.set_yticks(yticks)

def log_tick_labels(x, _):
    if x == 1e6:
        return r"$10^6$"
    elif x == 1e7:
        return r"$10^7$"
    elif x == 5e7:
        return r"$5\times10^7$"
    else:
        return ""

ax.yaxis.set_major_formatter(FuncFormatter(log_tick_labels))

# 6) Tick styling (white)
ax.tick_params(axis="y", which="major", length=5, width=1.2, colors="white")
ax.tick_params(axis="y", which="minor", length=5, width=0.8, colors="white")
ax.tick_params(axis="x", which="major", length=5, width=1.2, colors="white", labelsize=18)

# Make the left and bottom spines thinner
ax.spines['left'].set_linewidth(0.5)
ax.spines['bottom'].set_linewidth(0.5)

# Add a small margin around the data so axes don’t hug the corner
ax.margins(x=0.05, y=0.05)

# Move the bottom and left spines outward to create a visible gap
ax.spines['left'].set_position(('outward', 10))    # 10 points to the left
ax.spines['bottom'].set_position(('outward', 10))  # 10 points downward

# 6) Labels in white
ax.set_ylabel("AUC (RLU·h)", color="white", fontsize=14)
ax.set_xlabel("", color="white")

# 6) Auto‐limit to your data (with a little padding)
ymin = auc_df["AUC"].min() * 0.9
ymax = auc_df["AUC"].max() * 1.1
ax.set_ylim(ymin, ymax)

# 7) Annotate sample size under each box
group_counts = auc_df["base"].value_counts().loc[auc_df["base"].unique()]
for i, group in enumerate(auc_df["base"].unique()):
    ax.text(
        i, 0.01, f"N = {group_counts[group]}",
        ha="center", va="top",
        color="white", fontsize=12,
        transform=ax.get_xaxis_transform()
    )

# assume auc_df exists with columns base, replicate, AUC
group1, group2 = auc_df['base'].unique()
data1 = auc_df.loc[auc_df['base']==group1, 'AUC']
data2 = auc_df.loc[auc_df['base']==group2, 'AUC']

# geometric‐mean fold‐change
gm1 = np.exp(np.mean(np.log(data1)))
gm2 = np.exp(np.mean(np.log(data2)))
fold_change = gm2 / gm1

# t‑test on log10(AUC)
p_value = ttest_ind(np.log10(data2), np.log10(data1), equal_var=False).pvalue

# 2) Compute bar height just above your data
ymin = auc_df["AUC"].min()
bar_y = ymin * 0.98          # 5% above the highest point
cap_height = ymin * 0.01     # 2% of bar_y for the little caps

# 3) Draw a single comparison bar between the two groups (at x=0 and x=1)
x1, x2 = 0, 1

# horizontal line
ax.hlines(bar_y, x1, x2, color="white", linewidth=0.5, zorder=10)

# vertical end‐caps
ax.vlines([x1, x2], [bar_y, bar_y], [bar_y + cap_height, bar_y + cap_height],
          color="white", linewidth=0.5, zorder=10)


# 4) Annotate fold‐change and p‐value just below the bar
annotation = f"{fold_change:.1f}-fold, P = {p_value:.1e}"
ax.text(
    (x1 + x2) / 2,
    bar_y - cap_height * 1.5,
    annotation,
    ha="center", va="top",
    color="white", fontsize=16,
    zorder=11
)

#ax.set_title(
#    "Brightness Comparison",
#   color="white",
#    fontsize=16,
#    pad=15  # space between title and plot
#)

# 8) Save as transparent SVG
desktop = Path.home() / 'Desktop'
fig_path_svg = desktop / 'Bio_AUC_compare.svg'
plt.tight_layout()
plt.savefig(fig_path_svg, format="svg", transparent=True)
plt.show()

print("Saved figure to", fig_path_svg)

