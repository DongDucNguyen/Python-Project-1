import os
import time
import tracemalloc
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def read_data():
    file_path = os.path.join('P1_RES', 'results.csv')
    # Load the data
    df = pd.read_csv(file_path)

    # Columns that are not statistics
    non_numeric_cols = ['Name', 'Nation', 'Team', 'Position', 'Age']
    stats_cols = [col for col in df.columns if col not in non_numeric_cols]

    # Clean numeric columns (remove commas and convert to numbers)
    for col in stats_cols:
        df[col] = df[col].astype(str).str.replace(',', '', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce')

    return df, stats_cols, non_numeric_cols


def save_df_to_file(name, res):
    file_path = os.path.join('P2_RES', name)
    results_df = pd.DataFrame(res)
    results_df.to_csv(file_path, index=False, encoding='utf-8-sig')

def Find_Top_3(df, stats_cols):
    top3_results = []

    for col in stats_cols:
        if df[col].dropna().empty:
            continue  # Skip empty columns
        
        # Top 3 highest
        top_high = df[['Name', 'Team', col]].sort_values(by=col, ascending=False).head(3)
        
        # Top 3 lowest
        top_low = df[['Name', 'Team', col]].sort_values(by=col, ascending=True).head(3)
        
        section = f"=== {col} ===\n"
        section += "Top 3 Highest:\n"
        for idx, row in top_high.iterrows():
            section += f"  {row['Name']} ({row['Team']}): {row[col]}\n"
        
        section += "Top 3 Lowest:\n"
        for idx, row in top_low.iterrows():
            section += f"  {row['Name']} ({row['Team']}): {row[col]}\n"
        
        section += "\n"
        top3_results.append(section)

    # Save to top_3.txt
    file_path = os.path.join('P2_RES', 'top_3.txt')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(top3_results))

    print("top_3.txt saved!")

def Calculate_For_Each_Statistic(df, stats_cols):
    # Group by Team + one overall ("all")
    grouped = df.groupby('Team')
    summary_rows = []

    # First row: "all" players
    summary_all = {'Team': 'all'}
    for col in stats_cols:
        summary_all[f'Median of {col}'] = df[col].median()
        summary_all[f'Mean of {col}'] = df[col].mean()
        summary_all[f'Std of {col}'] = df[col].std()
    summary_rows.append(summary_all)

    # Each team's stats
    for team, team_df in grouped:
        summary_team = {'Team': team}
        for col in stats_cols:
            summary_team[f'Median of {col}'] = team_df[col].median()
            summary_team[f'Mean of {col}'] = team_df[col].mean()
            summary_team[f'Std of {col}'] = team_df[col].std()
        summary_rows.append(summary_team)

    # Save to results2.csv
    save_df_to_file('results2.csv', summary_rows)
    print("results2.csv saved!")

def Histograms_Entire_League(df, valid_indexes):
    print("\n--- Plotting Overall League Distributions ---")
    num_valid_indexes = len(valid_indexes)
    # Calculate grid size for overall plots (e.g., 2 columns)
    ncols_overall = 2
    nrows_overall = (num_valid_indexes + ncols_overall - 1) // ncols_overall

    plt.figure(figsize=(12, 5 * nrows_overall))
    plt.suptitle('Overall League Distribution of Player Indexes', fontsize=16, y=1.02) # Add space with y

    for i, index_col in enumerate(valid_indexes):
        plt.subplot(nrows_overall, ncols_overall, i + 1)
        # Filter out NaN values for plotting if you didn't fill them earlier
        data_to_plot = df[index_col].dropna()
        if not data_to_plot.empty:
            sns.histplot(data_to_plot, kde=True, bins=20)
            plt.title(f'Distribution of {index_col}')
            plt.xlabel(index_col)
            plt.ylabel('Frequency')
        else:
            plt.title(f'{index_col}\n(No valid data to plot)')

    plt.tight_layout(rect=[0, 0, 1, 0.98]) # Adjust layout to prevent overlap with suptitle
    plt.savefig(os.path.join('P2_RES', 'Overall_League_Distribution_of_Player_Indexes.png'))
    print("\n--- Done Plotting Overall League Distributions ---")

def Histograms_per_Team(df, team_column_name, valid_indexes, max_teams_per_row_facet):
    print("\n--- Plotting Per-Team Distributions ---")

    # Check number of unique teams to avoid overly large grids
    unique_teams = df[team_column_name].nunique()
    print(f"Found {unique_teams} unique teams.")
    if unique_teams > 50: # Add a threshold to prevent overwhelming plots
        print("Warning: High number of teams detected. FacetGrid might be very large.")
        # Optional: Add logic here to maybe plot only a subset of teams or ask user

    for index_col in valid_indexes:
        print(f"Generating FacetGrid for: {index_col}")

        # Filter out NaNs for this specific index and the team column before creating the grid
        facet_data = df[[index_col, team_column_name]].dropna()

        if facet_data.empty or facet_data[index_col].isnull().all():
            print(f"  Skipping {index_col} - No valid data after dropping NaNs.")
            continue

        # Create the FacetGrid
        g = sns.FacetGrid(
            facet_data,
            col=team_column_name,
            col_wrap=min(max_teams_per_row_facet, unique_teams), # Don't wrap more than teams exist
            sharex=True, # Keep x-axis consistent for comparison
            sharey=False, # Allow y-axis (frequency) to vary per team
            height=3,    # Adjust height of each subplot
            aspect=1.2   # Adjust aspect ratio of each subplot
        )

        # Map the histogram plot onto the grid
        g.map(sns.histplot, index_col, kde=True, bins=15) # Use fewer bins for smaller plots

        # Add titles and adjust layout
        g.set_titles("Team: {col_name}")
        g.fig.suptitle(f'Distribution of {index_col.split} by Team', fontsize=14, y=1.03) # Add overall title slightly above
        g.fig.tight_layout(rect=[0, 0, 1, 0.97]) # Adjust layout
        name = (index_col.replace(' ', '_')).replace(':', '')
        plt.savefig(os.path.join('P2_RES','Distribution_of_'+name+'_by_Team.png'))
    print("\n--- Done Plotting Per-Team Distributions ---")

def Plotting(df):
    # --- Setting up ---
    attack_indexes = [
        'Performance: goals',  
        'Performance: assists', 
        'Expected: expected goals (xG)'
    ]

    defense_indexes = [
        'Tackles: Tkl', 
        'Challenges: Att', 
        'Blocks: Blocks'   
    ]

    team_column_name = 'Team'
    max_teams_per_row_facet = 4 # How many team plots per row in FacetGrid

    all_indexes = attack_indexes + defense_indexes
    valid_indexes = []

    for col in all_indexes:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            if not df[col].isnull().all() and pd.api.types.is_numeric_dtype(df[col]):
                valid_indexes.append(col)

    # --- Plotting ---

    # 1. Histograms for the Entire League
    Histograms_Entire_League(df, valid_indexes)
    
    # 2. Histograms per Team (using FacetGrid)
    Histograms_per_Team(df, team_column_name, valid_indexes, max_teams_per_row_facet)
    
    print("\n--- Plotting Complete ---")

def Best_Team_Summary(df, stats_cols):
    # Group by Team
    grouped_team = df.groupby('Team')

    # Store the best team per stat
    best_team_per_stat = {}

    for col in stats_cols:
        if df[col].dropna().empty:
            continue
        # Calculate mean per team
        mean_per_team = grouped_team[col].mean()
        best_team = mean_per_team.idxmax()  # Team with highest mean
        best_score = mean_per_team.max()
        best_team_per_stat[col] = (best_team, best_score)

    # Count how many times each team was best
    from collections import Counter
    team_counter = Counter([team for team, score in best_team_per_stat.values()])

    # Find the team that was best most often
    best_overall_team, count = team_counter.most_common(1)[0]

    # Save results
    file_path = os.path.join('P2_RES', 'best_team_summary.txt')
    data = []

    for stat, (team, score) in best_team_per_stat.items():
        data.append({
            'Statistic': stat,
            'Best Team': team,
            'Average Score': round(score, 2)
        })

    df = pd.DataFrame(data)

    overall_row = {
        'Statistic': 'Best Overall Team',
        'Best Team': best_overall_team,
        'Average Score': f'Top in {count} statistics'
    }

    df = pd.concat([df, pd.DataFrame([overall_row])], ignore_index=True)
    df.to_csv(file_path, index=False, sep='\t')
    print(f"Best team identified: {best_overall_team} (Top in {count} stats). See 'best_team_summary.txt'.")

def Problem_2():
    df, stats_cols, non_numeric_cols = read_data()
    # 1. Find top 3 highest and lowest for each statistic
    Find_Top_3(df, stats_cols)
    # 2. Calculate Median, Mean, Std for each statistic
    Calculate_For_Each_Statistic(df, stats_cols)
    # 3. Plotting
    Plotting(df)
    # 4. Identify the best team for each statistic
    Best_Team_Summary(df, stats_cols)

if __name__ =='__main__':
    tracemalloc.start()
    start = time.time()
    os.makedirs('P2_RES', exist_ok=True)
    Problem_2()
    end = time.time()
    print(f"Thời gian chạy: {end - start:.6f} giây")
    current, peak = tracemalloc.get_traced_memory()
    print(f"Bộ nhớ hiện tại: {current / 1024 ** 2:.2f} MB")
    print(f"Bộ nhớ đạt đỉnh: {peak / 1024 ** 2:.2f} MB")
    tracemalloc.stop()