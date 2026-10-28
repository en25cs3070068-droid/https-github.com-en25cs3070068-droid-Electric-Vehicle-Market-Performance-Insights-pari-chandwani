
from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import plotly.io as pio

app = Flask(__name__, template_folder=".")
DATA_FILE = "ev_market_test.csv"

@app.route("/")
def dashboard():
    df = pd.read_csv(DATA_FILE)

    manufacturer = request.args.get("manufacturer", "All")
    battery_type = request.args.get("battery_type", "All")
    category = request.args.get("category", "All")
    region = request.args.get("region", "All")

    if manufacturer != "All":
        df = df[df["manufacturer"] == manufacturer]
    if battery_type != "All":
        df = df[df["battery_type"] == battery_type]
    if category != "All":
        df = df[df["category"] == category]
    if region != "All":
        df = df[df["market_region"] == region]

    total_vehicles = len(df)
    total_sales = df["annual_sales_units"].sum()
    avg_range = round(df["range_km"].mean(), 1) if len(df) else 0
    avg_rating = round(df["customer_rating"].mean(), 2) if len(df) else 0
    avg_price = round(df["price_usd"].mean(), 0) if len(df) else 0

    sales = (df.groupby("manufacturer", as_index=False)
             ["annual_sales_units"].sum()
             .sort_values("annual_sales_units", ascending=False)
             .head(10))

    battery = df.groupby("battery_type").size().reset_index(name="count")
    categories = df.groupby("category", as_index=False)["annual_sales_units"].sum()
    ratings = (df.groupby("manufacturer", as_index=False)["customer_rating"].mean()
               .sort_values("customer_rating", ascending=False).head(10))

    scatter = df.groupby("model_name", as_index=False).agg(
        range_km=("range_km", "mean"),
        price_usd=("price_usd", "mean"),
        manufacturer=("manufacturer", "first"),
        category=("category", "first")
    )

    def chart_html(fig):
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#111827",
            plot_bgcolor="#111827",
            font_color="#E5E7EB",
            margin=dict(l=25, r=20, t=60, b=35),
            title_font_size=17
        )
        return pio.to_html(
            fig, full_html=False, include_plotlyjs="cdn",
            config={"responsive": True, "displaylogo": False}
        )

    sales_chart = chart_html(px.bar(
        sales, x="manufacturer", y="annual_sales_units",
        color="annual_sales_units", title="Top Manufacturers by Sales",
        labels={"annual_sales_units": "Annual Sales", "manufacturer": "Manufacturer"}
    ))

    battery_chart = chart_html(px.pie(
        battery, names="battery_type", values="count",
        hole=0.55, title="Battery Technology Distribution"
    ))

    category_chart = chart_html(px.bar(
        categories, x="category", y="annual_sales_units",
        color="category", title="Sales by Vehicle Category",
        labels={"annual_sales_units": "Annual Sales", "category": "Category"}
    ))

    rating_chart = chart_html(px.bar(
        ratings, x="manufacturer", y="customer_rating",
        color="customer_rating", title="Top Manufacturer Ratings",
        labels={"customer_rating": "Average Rating"}
    ))

    scatter_chart = chart_html(px.scatter(
        scatter, x="price_usd", y="range_km",
        color="category", hover_name="model_name",
        hover_data=["manufacturer"],
        title="Vehicle Price vs Driving Range",
        labels={"price_usd": "Price (USD)", "range_km": "Range (km)"}
    ))

    return render_template(
        "index.html",
        total_vehicles=f"{total_vehicles:,}",
        total_sales=f"{total_sales:,.0f}",
        avg_range=avg_range,
        avg_rating=avg_rating,
        avg_price=f"${avg_price:,.0f}",
        sales_chart=sales_chart,
        battery_chart=battery_chart,
        category_chart=category_chart,
        rating_chart=rating_chart,
        scatter_chart=scatter_chart,
        manufacturers=sorted(pd.read_csv(DATA_FILE)["manufacturer"].dropna().unique()),
        batteries=sorted(pd.read_csv(DATA_FILE)["battery_type"].dropna().unique()),
        categories_list=sorted(pd.read_csv(DATA_FILE)["category"].dropna().unique()),
        regions=sorted(pd.read_csv(DATA_FILE)["market_region"].dropna().unique()),
        selected_manufacturer=manufacturer,
        selected_battery=battery_type,
        selected_category=category,
        selected_region=region
    )

if __name__ == "__main__":
    app.run(debug=True)



