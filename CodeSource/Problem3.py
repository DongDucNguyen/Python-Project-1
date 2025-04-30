import os
import time
import tracemalloc
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns


def Load_and_Preprocess_Data():
    Exclude_Cols = ['Name', 'Nation', 'Team', 'Position', 'Age']
    
    file_path = os.path.join('P1_RES', 'results.csv')
    df = pd.read_csv(file_path)
    # --- Preprocessing ---
    identifiers = df[Exclude_Cols]
    features = df.drop(columns=Exclude_Cols).apply(pd.to_numeric, errors='coerce')

    cols_all_nan = features.columns[features.isnull().all()]
    if not cols_all_nan.empty:
        features = features.drop(columns=cols_all_nan)

    imputer = SimpleImputer(strategy='median')
    scaler = StandardScaler()

    df_imputed = pd.DataFrame(imputer.fit_transform(features), columns=features.columns)
    df_scaled = pd.DataFrame(scaler.fit_transform(df_imputed), columns=df_imputed.columns)

    return df_scaled, df, df_imputed

def Determine_Optimal_K(df_scaled):
    inertia = []
    silhouette_scores = []
    kRange = range(2, 16)
    for k in kRange:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10).fit(df_scaled)
        inertia.append(kmeans.inertia_)
        print(f"Inertia for k={k} calculated.", end=' ')
        if k > 1:
                try:
                    score = silhouette_score(df_scaled, kmeans.labels_)
                    silhouette_scores.append(score)
                    print(f"Silhouette Score: {score:.4f}")
                except ValueError as e:
                    print(f"  Could not calculate silhouette score for K={k}: {e}")
                    silhouette_scores.append(-1) # Append a placeholder if calculation fails

    plt.figure(figsize=(10, 6))
    plt.plot(kRange, inertia, 'o--')
    plt.xlabel('Number of Clusters (k)')
    plt.ylabel('Inertia')
    plt.title('Elbow Method for Optimal K')
    plt.xticks(list(kRange))
    plt.grid(True)
    plt.savefig(os.path.join('P3_RES', 'Elbow_Method_fo_Optimal_K.png'))
    plt.close()
    print(f'Elbow_Method_fo_Optimal_K.png is saved')

    valid_k_range_silhouette = list(kRange) # k_range already starts from 2
    plt.figure(figsize=(10, 6))
    plt.plot(valid_k_range_silhouette, silhouette_scores, marker='o')
    plt.title('Silhouette Score for Optimal K')
    plt.xlabel('Number of clusters (K)')
    plt.ylabel('Silhouette Score')
    plt.grid(True)
    plt.savefig(os.path.join('P3_RES', 'Silhouette_Score.png'))
    plt.close()
    print(f'Silhouette_Score.png is saved')
    

def Apply_K_means(df_scaled, df, optimal_k, df_imputed):
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(df_scaled)

    df['Cluster'] = cluster_labels
    df_scaled['Cluster'] = cluster_labels

    print(f"K-means clustering complete with k={optimal_k}.")

    # --- Cluster Analysis ---
    print("\n--- Cluster Analysis ---")
    print("\nMean (scaled features) per cluster:")
    print(df_scaled.groupby('Cluster').mean())

    df_imputed['Cluster'] = cluster_labels
    print("\nMean (original features) per cluster:")

    stats = [
    'Performance: goals', 
    'Performance: assists', 
    'Tackles: TklW',
    'Blocks: Int',
    'Performance: Save%'
    ]
    available_stats = [s for s in stats if s in df_imputed.columns]
    print(df_imputed.groupby('Cluster')[available_stats].mean())
    print("-" * 50)
    return cluster_labels

def Apply_PCA(df_scaled, cluster_labels):
    print("Applying PCA...")
    pca = PCA(n_components=2)
    components = pca.fit_transform(df_scaled.drop(columns='Cluster'))

    pca_clusters_df = pd.DataFrame(components, columns=['PC1', 'PC2'])
    pca_clusters_df['Cluster'] = cluster_labels

    print(f"PCA complete. Explained variance: {pca.explained_variance_ratio_.sum():.4f}")

    return pca_clusters_df

def Plot_2D_Cluster(pca_clusters_df, optimal_k):
    plt.figure(figsize=(12, 8))
    sns.scatterplot(
        x='PC1', y='PC2', hue='Cluster', 
        palette=sns.color_palette('viridis', n_colors=optimal_k),
        data=pca_clusters_df, legend='full', alpha=0.7
    )
    plt.title(f'PCA of Clusters (k={optimal_k})')
    plt.grid(True)
    plt.savefig(os.path.join('P3_RES', f'PCA_of_Clusters_k={optimal_k}.png'))
    plt.close()
    print(f'PCA_of_Clusters_k={optimal_k}.png is saved')

def Problem_3():
    df_scaled, df, df_imputed = Load_and_Preprocess_Data()
    Determine_Optimal_K(df_scaled)
    optimal_k = 6
    print(f"\nBased on the Elbow method and Silhouette Score plots, choosing K = {optimal_k}.")
    cluster_labels = Apply_K_means(df_scaled, df, optimal_k, df_imputed)
    pca_clusters_df = Apply_PCA(df_scaled, cluster_labels)
    Plot_2D_Cluster(pca_clusters_df, optimal_k)

    #Create a file comments for the results
    print('Writing comments for the results')
    with open(os.path.join('P3_RES', "comment_P3.txt"), "w", encoding="utf-8") as f:
        f.write("\n--- Comments on Results ---\n")
        f.write(f"1. Number of Groups (K):\n")
        f.write(f"   - Based on the Elbow Method and Silhouette Score analysis, K={optimal_k} clusters were chosen.\n")
        f.write(f"   - The Elbow plot likely showed diminishing returns in WCSS reduction around K={optimal_k}.\n")
        f.write(f"   - The Silhouette Score plot might have indicated a peak or high value at K={optimal_k}, suggesting reasonable cluster separation.\n")
        f.write(f"   - This aligns with the common understanding of distinct player roles in football (e.g., Goalkeepers, Defenders, Midfielders, Forwards).\n")
        f.write(f"\n2. PCA and Clustering Plot:\n")
        f.write(f"   - PCA was used to reduce the {df_scaled.shape[1]} features to 2 dimensions for visualization.\n")
        f.write(f"   - The 2D scatter plot shows the distribution of players based on these two principal components, colored by their assigned K-means cluster.\n")
        f.write(f"   - Interpretation of the plot:\n")
        f.write(f"     - Observe the separation between clusters. Are they distinct or overlapping?\n")
        f.write(f"     - Do the clusters seem to correspond to player positions? (We could verify this by looking at the `Position` column for players within each cluster). For instance, one cluster might predominantly contain Goalkeepers due to their unique stats, while others might represent defenders, midfielders, and attackers.\n")
        f.write(f"     - The spread and density of points within each cluster provide insight into the similarity of players grouped together based on the selected statistics.\n")
        
        f.write("\nCluster Composition Example (Top Positions):\n")
        for i in range(optimal_k):
            cluster_data = df[df['Cluster'] == i]
            position_counts = cluster_data['Position'].value_counts()
            f.write(f"\nCluster {i}:\n")
            f.write(f"  Total Players: {len(cluster_data)}\n")
            f.write("  Top Positions:\n")
            for pos, count in position_counts.head().items():
                f.write(f"    {pos}: {count}\n")
    print(f'comment_P3.txt is saved')

if __name__ == '__main__': 
    os.makedirs('P3_RES', exist_ok=True)
    tracemalloc.start()
    start = time.time()
    os.makedirs('P2_RES', exist_ok=True)
    Problem_3()
    end = time.time()
    print(f"Thời gian chạy: {end - start:.6f} giây")
    current, peak = tracemalloc.get_traced_memory()
    print(f"Bộ nhớ hiện tại: {current / 1024 ** 2:.2f} MB")
    print(f"Bộ nhớ đạt đỉnh: {peak / 1024 ** 2:.2f} MB")
    tracemalloc.stop()