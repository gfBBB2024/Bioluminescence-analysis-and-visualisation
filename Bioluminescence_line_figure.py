import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.ticker import FuncFormatter
import numpy as np

file_path = '/Users/fg221/Library/CloudStorage/OneDrive-ImperialCollegeLondon/PhD Milestone/PhD thesis/Engineering a Brighter Bacterial Bioluminescence Pathway/exp_comparison_ilux2lux_gly5315/Data process_27072025.xlsx'
xls = pd.ExcelFile(file_path)
#print(xls.sheet_names)
df_lum = pd.read_excel(file_path, sheet_name="data_to_code")
#print(df_full_spectra.head(2))

value_vars_full = [col for col in df_lum.columns if col != 'Time, h']
df_brightness = df_lum.melt(
    id_vars=['Time, h'],        # keep this column fixed
    value_vars=value_vars_full,  # stack every other column
    var_name='construct',     # name for the “former column‑headers”
    value_name='lum'         # name for the “former cell values”
)
#print(df_brightness.head())


df_long = df_brightness

#Create a base‐reporter column by dropping the ".N" suffix:
df_long['construct_base'] = (
   df_long['construct'].str.replace(r'\.\d+$', '', regex=True)
)

#print(df_long.head(100))

sns.set_theme(style="white")


#Plot mean ± 1 SD using Seaborn’s built‑in error‐bar support
plt.figure(figsize=(6, 6), facecolor='none')

palette_map = {
    "ilux2lux": "#cb9e59",
    "gly5315": "#ebe05e",
}

ax = sns.lineplot(
    data=df_long,
    x='Time, h',
    y='lum',
    hue='construct_base',
    estimator='mean',     # compute mean for each (time, reporter)
    ci='sd',              # draw ±1 SD around the mean
    palette=palette_map,             
    lw=2                  # line width
)

ax.set_facecolor('none')   # transparent plotting area
sns.despine(trim=True)


leg = ax.legend(
    title='',               # no title
    frameon=True,           # we’ll customize the frame
    loc='upper left',
    bbox_to_anchor=(0,1)
)

# make the legend box transparent
frame = leg.get_frame()
frame.set_facecolor('none')   # no background
frame.set_edgecolor('none')   # no border

for text in leg.get_texts():
    text.set_color('white')

ax.set_title(
    "Intensity",
    color='white',
    fontsize=16,
    pad=15  # space between title and plot
)

# Axis spine and tick colors
for spine in ax.spines.values():
    spine.set_edgecolor('white')
ax.tick_params(colors='white', which='both')

# Axis labels in white
ax.xaxis.label.set_color('white')
ax.yaxis.label.set_color('white')
ax.set_xlabel('Time, h', fontsize=18)
ax.set_ylabel('Luminescence, RLU', fontsize=18)

# Tick‐label size (applies to both axes):
ax.tick_params(axis='both', which='major', labelsize=14)

# Spine (axis line) width:
# you can do only bottom & left, or all four if you like
ax.spines['bottom'].set_linewidth(0.5)
ax.spines['left'].set_linewidth(0.5)

x_ticks = [0, 5, 10, 15, 20, 25]
ax.set_xticks(x_ticks)


# Set y-axis to log scale
ax.set_yscale("log")

# Set y-axis limits
ax.set_ylim(1e6, 5e7)  # From 1×10⁶ to 5×10⁷

# Set tick positions at powers of 10 (adjust if needed)
yticks = [1e6, 1e7, 5e7]
ax.set_yticks(yticks)

# Only label selected ticks
def log_tick_labels(x, _):
    if x == 1e6:
        return r"$10^6$"
    elif x == 1e7:
        return r"$10^7$"
    elif x == 1e8:
        return r"$10^8$"
    else:
        return ""

ax.yaxis.set_major_formatter(FuncFormatter(log_tick_labels))

#Force ticks onto the bottom & left spines:
ax.xaxis.set_ticks_position('bottom')
ax.yaxis.set_ticks_position('left')

for axis in ['x', 'y']:
    ax.tick_params(axis=axis, which='major', length=5, width=0.5)
    ax.tick_params(axis=axis, which='minor', length=3, width=0.5)

sns.despine(trim=True)
plt.tight_layout()

desktop = Path.home() / 'Desktop'
fig_path_svg = desktop / 'Bio_compare.svg'
plt.savefig(fig_path_svg, transparent=True, bbox_inches='tight', format='svg')
plt.show()