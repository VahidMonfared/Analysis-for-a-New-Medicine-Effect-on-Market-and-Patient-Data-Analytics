import pandas as pd
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset
file_path = '/mnt/data/Case Study Raw Data File .xlsx'
df = pd.read_excel(file_path, sheet_name='raw', skiprows=1)

# Rename columns
df.columns = [
    "HCP_ID", "NBRx_2021_07", "NBRx_2021_08", "NBRx_2021_09", "NBRx_2021_10", "NBRx_2021_11", "NBRx_2021_12",
    "NBRx_2022_01", "NBRx_2022_02", "NBRx_2022_03", "NBRx_2022_04", "NBRx_2022_05", "NBRx_2022_06",
    "NBRx_2022_07", "NBRx_2022_08", "NBRx_2022_09", "NBRx_2022_10", "NBRx_2022_11", "NBRx_2022_12",
    "NBRx_unused_1", "NBRx_unused_2", "NBRx_unused_3", "NBRx_unused_4", "NBRx_unused_5", "NBRx_unused_6",
    "Calls_2022_01", "Calls_2022_02", "Calls_2022_03", "Calls_2022_04", "Calls_2022_05", "Calls_2022_06",
    "Calls_2022_07", "Calls_2022_08", "Calls_2022_09", "Calls_2022_10", "Calls_2022_11", "Calls_2022_12",
    "Region", "Segment", "Message"
]

# Convert columns to numeric
for col in df.columns[1:-3]:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Define pilot regions
pilot_regions = [3, 7]

# Define pre- and post-initiative months
pre_months = [f'NBRx_2022_0{i}' for i in range(1, 7)]
post_months = [f'NBRx_2022_0{i}' for i in range(7, 10)] + [f'NBRx_2022_10', 'NBRx_2022_11', 'NBRx_2022_12']

# Calculate pre and post averages
df['pre_avg'] = df[pre_months].mean(axis=1)
df['post_avg'] = df[post_months].mean(axis=1)
df['delta_nbrx'] = df['post_avg'] - df['pre_avg']

# Create flags
df['is_pilot'] = df['Region'].isin(pilot_regions)
df['is_advocate'] = df['Segment'] == 'Patient Advocate'
df['is_segmented'] = df['Message'] == 'Segmented'

# Filter for patient advocates in pilot regions
pa_pilot = df[df['is_pilot'] & df['is_advocate']]

# T-test between segmented and standard
segmented = pa_pilot[pa_pilot['is_segmented']]['delta_nbrx']
standard = pa_pilot[~pa_pilot['is_segmented']]['delta_nbrx']
t_stat, p_val = ttest_ind(segmented, standard, nan_policy='omit')

# Boxplot visualization
plt.figure(figsize=(8, 5))
sns.boxplot(x='Message', y='delta_nbrx', data=pa_pilot)
plt.title('Change in NBRx by Message Type\n(Patient Advocates in Pilot Regions)')
plt.axhline(0, color='red', linestyle='--')
plt.tight_layout()
plt.savefig("/mnt/data/Change_NBRx_Boxplot.png")

# Summary conclusion
result = {
    "Segmented Avg ΔNBRx": segmented.mean(),
    "Standard Avg ΔNBRx": standard.mean(),
    "T-Statistic": t_stat,
    "P-Value": p_val,
    "Was Initiative Successful?": "Yes" if p_val < 0.05 else "No",
    "Recommendation": "Rollout Segmentation" if p_val < 0.05 and segmented.mean() > standard.mean() else "Do Not Rollout Yet"
}

summary_df = pd.DataFrame([result])
import ace_tools as tools; tools.display_dataframe_to_user(name="Case Study Results Summary", dataframe=summary_df)
