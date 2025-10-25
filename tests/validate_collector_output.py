"""
validate_collector_output.py
-------------------------------------
Validation & health check for collector output.

Outputs:
- total record count
- duplicates removed
- per-keyword + per-platform summary
- sentiment diagnostics
- missing / weak keyword report
-------------------------------------
Author: ChatGPT (for Rob)
"""

import pandas as pd
from pathlib import Path
from rich.console import Console
from rich.table import Table
import matplotlib.pyplot as plt

console = Console()
FILE = Path("social_posts.csv")


def validate_collector_output(csv_path: str = None):
    """
    Validate collector output and generate diagnostics.

    Args:
        csv_path: Path to CSV file (default: social_posts.csv)

    Returns:
        dict: Validation results
    """
    if csv_path:
        file = Path(csv_path)
    else:
        file = FILE

    if not file.exists():
        console.print("[bold red]❌ social_posts.csv not found. Run message_collector_v2.py first.[/bold red]")
        return {
            "success": False,
            "error": "CSV file not found",
            "total_posts": 0,
            "weak_keywords": []
        }

    # --- Load and clean ---
    df = pd.read_csv(file)
    console.print(f"[bold cyan]Loaded {len(df)} records from {file}[/bold cyan]")

    if "text_excerpt" not in df.columns:
        console.print("[red]❌ Missing 'text_excerpt' column. Check collector output.[/red]")
        return {
            "success": False,
            "error": "Missing text_excerpt column",
            "total_posts": len(df),
            "weak_keywords": []
        }

    # Remove blank or NaN rows
    initial_count = len(df)
    df.dropna(subset=["text_excerpt"], inplace=True)
    df.drop_duplicates(subset=["text_excerpt"], inplace=True)
    final_count = len(df)
    console.print(f"[green]After cleaning: {final_count} unique posts (removed {initial_count - final_count} duplicates)[/green]")

    # --- Summary by platform ---
    table = Table(title="Records by Platform")
    table.add_column("Platform", style="cyan")
    table.add_column("Count", style="yellow")
    table.add_column("Avg Sentiment", style="magenta")

    platform_data = {}
    for plat, group in df.groupby("platform"):
        avg_sent = round(group["sentiment"].mean(), 3) if "sentiment" in group else 0
        table.add_row(plat, str(len(group)), str(avg_sent))
        platform_data[plat] = {
            "count": len(group),
            "avg_sentiment": avg_sent
        }
    console.print(table)

    # --- Summary by keyword ---
    kw_table = Table(title="Records by Keyword (Top 10)")
    kw_table.add_column("Keyword", style="cyan")
    kw_table.add_column("Count", style="yellow")
    kw_table.add_column("Avg Sentiment", style="magenta")

    kw_counts = (
        df.groupby("keyword")
          .agg(count=("text_excerpt", "size"), mean_sent=("sentiment", "mean"))
          .sort_values("count", ascending=False)
    )

    for kw, row in kw_counts.head(10).iterrows():
        kw_table.add_row(kw, str(int(row["count"])), f"{row['mean_sent']:.3f}")
    console.print(kw_table)

    # --- Detect weak or missing keywords ---
    missing_kw = kw_counts[kw_counts["count"] < 3].index.tolist()
    if missing_kw:
        console.print("[bold yellow]⚠️ Weak keywords (less than 3 records):[/bold yellow]")
        for kw in missing_kw:
            console.print(f"   - {kw}")

    # --- Sentiment distribution plot ---
    if "sentiment" in df.columns and not df["sentiment"].isna().all():
        plt.figure(figsize=(7, 4))
        df["sentiment"].hist(bins=20, color="skyblue", edgecolor="black")
        plt.title("Sentiment Distribution")
        plt.xlabel("Sentiment (-1 negative → +1 positive)")
        plt.ylabel("Frequency")
        plt.tight_layout()
        output_dir = file.parent
        sentiment_path = output_dir / "sentiment_histogram.png"
        plt.savefig(sentiment_path)
        plt.close()
        console.print(f"[green]📊 Saved histogram → {sentiment_path}[/green]")
    else:
        console.print("[yellow]⚠️ No sentiment column detected.[/yellow]")

    # --- Keyword coverage bar chart ---
    plt.figure(figsize=(8, 6))
    kw_counts["count"].plot(kind="barh", color="lightgreen", title="Posts per Keyword")
    plt.tight_layout()
    coverage_path = output_dir / "keyword_coverage.png"
    plt.savefig(coverage_path)
    plt.close()
    console.print(f"[green]📈 Saved keyword coverage chart → {coverage_path}[/green]")

    # --- Validation results ---
    sentiment_variance = df["sentiment"].var() if "sentiment" in df.columns else 0

    validation_results = {
        "success": True,
        "total_posts": final_count,
        "duplicates_removed": initial_count - final_count,
        "platforms": platform_data,
        "weak_keywords": missing_kw,
        "sentiment_variance": round(sentiment_variance, 3),
        "charts_generated": True
    }

    # --- Quality gates ---
    console.print("\n[bold]Quality Gate Results:[/bold]")

    if final_count >= 200:
        console.print("[green]✅ Total posts >= 200 (EXCELLENT)[/green]")
    elif final_count >= 100:
        console.print("[yellow]⚠️ Total posts >= 100 (GOOD, aim for 200+)[/yellow]")
    elif final_count >= 50:
        console.print("[yellow]⚠️ Total posts >= 50 (MARGINAL, expand keywords)[/yellow]")
    else:
        console.print("[red]❌ Total posts < 50 (INSUFFICIENT, expand keywords/date)[/red]")
        validation_results["success"] = False

    if len(missing_kw) <= 2:
        console.print(f"[green]✅ Weak keywords: {len(missing_kw)} (ACCEPTABLE)[/green]")
    elif len(missing_kw) <= 5:
        console.print(f"[yellow]⚠️ Weak keywords: {len(missing_kw)} (REVIEW NEEDED)[/yellow]")
    else:
        console.print(f"[red]❌ Weak keywords: {len(missing_kw)} (TOO MANY, replace keywords)[/red]")

    if len(platform_data) >= 2:
        console.print("[green]✅ Multiple platforms active (GOOD)[/green]")
    else:
        console.print("[yellow]⚠️ Only one platform active (check API credentials)[/yellow]")

    if sentiment_variance >= 0.2:
        console.print("[green]✅ Sentiment variance >= 0.2 (DIVERSE)[/green]")
    else:
        console.print("[yellow]⚠️ Low sentiment variance (data may be too narrow)[/yellow]")

    console.print("[bold green]✅ Validation complete.[/bold green]")

    return validation_results


if __name__ == "__main__":
    results = validate_collector_output()
    print(f"\nValidation success: {results['success']}")
    print(f"Total posts: {results['total_posts']}")
    print(f"Weak keywords: {len(results['weak_keywords'])}")
