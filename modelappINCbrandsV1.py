import streamlit as st
from math import sqrt
from scipy.stats import norm

# Inject custom CSS for nicer UI and larger text
st.markdown(
    """
    <style>
    .big-font {font-size: 20px !important; }
    .header-font {font-size: 28px !important; font-weight: bold; }
    .subheader-font {font-size: 24px !important; font-weight: bold; }
    </style>
    """,
    unsafe_allow_html=True
)

# =============================================================================
# Global Parameters
# =============================================================================
st.markdown("<p class='header-font'>Supply Chain & Inventory Model Setup</p>", unsafe_allow_html=True)

interest_rate = st.number_input(
    "Actual Interest Rate (%)",
    min_value=0.0,
    max_value=100.0,
    value=5.0,
    step=0.1
)

service_level = st.slider(
    "Required Service Level (0-1)",
    min_value=0.0,
    max_value=1.0,
    value=0.95
)

layout_type = st.radio(
    "Layout Type",
    options=["Central and Fronts", "Main Regionals"]
)

if layout_type == "Main Regionals":
    st.info("Note: With 'Main Regionals', all warehouses must be of type MAIN.")

unit_cost = st.number_input(
    "Unit (4 Panels) Cost (per unit, in $)",
    min_value=0.0,
    value=80.0,
    step=1.0,
)

# Calculate Z_value from service_level
Z_value = norm.ppf(service_level)

# =============================================================================
# Rental Parameters
# =============================================================================
st.markdown("<p class='subheader-font'>Rental Parameters</p>", unsafe_allow_html=True)

sq_ft_per_unit = st.number_input(
    "Square feet required per unit (4 Panels) - (default 0.8)",
    min_value=0.0,
    value=0.8,
    step=0.1,
    format="%.1f"
)

overhead_factor_main = st.number_input(
    "Overhead factor for MAIN warehouse (default 1.2)",
    min_value=1.0,
    value=1.2,
    step=0.1,
    format="%.1f"
)

overhead_factor_front = st.number_input(
    "Overhead factor for FRONT warehouse (default 1.5)",
    min_value=1.0,
    value=1.5,
    step=0.1,
    format="%.1f"
)

# =============================================================================
# Market Areas Setup (with Brands)
# =============================================================================
st.markdown("<p class='subheader-font'>Market Areas Setup</p>", unsafe_allow_html=True)

base_market_areas = ["FL", "CA_SOUTH", "CA_NORTH", "TX", "NJ"]
st.write("Standard market areas:", base_market_areas)

custom_market_areas_str = st.text_input("Enter additional market areas (comma separated)", value="")
custom_market_areas = [area.strip() for area in custom_market_areas_str.split(",") if area.strip() != ""]

all_market_areas = list(dict.fromkeys(base_market_areas + custom_market_areas))
selected_market_areas = st.multiselect("Select Market Areas to use", options=all_market_areas, default=all_market_areas)

# For each market area, נציג קלט באמצעות עמודות לכל אחד משלושת המותגים
market_data = {}
brand_list = ["Heliocol", "SunStar", "SunValue"]

for area in selected_market_areas:
    st.markdown(f"### Parameters for Market Area: {area}", unsafe_allow_html=True)
    cols = st.columns(3)
    brand_data = {}
    for i, brand in enumerate(brand_list):
        with cols[i]:
            st.markdown(f"**{brand}**")
            avg_order_size = st.number_input(
                "Avg Order Size",
                min_value=0,
                value=100,
                step=1,
                key=f"{area}_{brand}_aos"
            )
            avg_daily_demand = st.number_input(
                "Avg Daily Demand",
                min_value=0,
                value=50,
                step=1,
                key=f"{area}_{brand}_add"
            )
            std_daily_demand = st.number_input(
                "Std Daily Demand",
                min_value=0.0,
                value=10.0,
                step=0.1,
                key=f"{area}_{brand}_std"
            )
            st.markdown("**12-Month Forecast Demand**")
            forecast_demand = []
            for m in range(12):
                f_val = st.number_input(
                    f"Month {m+1}",
                    min_value=0,
                    value=0,
                    step=1,
                    key=f"{area}_{brand}_m{m+1}"
                )
                forecast_demand.append(f_val)
            brand_data[brand] = {
                "avg_order_size": avg_order_size,
                "avg_daily_demand": avg_daily_demand,
                "std_daily_demand": std_daily_demand,
                "forecast_demand": forecast_demand
            }
    market_data[area] = brand_data

# Assign the collected data to market_area_data for downstream use
market_area_data = market_data

# =============================================================================
# Warehouse Setup
# =============================================================================
st.markdown("<p class='subheader-font'>Warehouse Setup</p>", unsafe_allow_html=True)

base_warehouse_locations = ["FL", "CA_SOUTH", "CA_NORTH", "TX", "NJ"]
st.write("Standard warehouse locations:", base_market_areas)

custom_warehouse_locations_str = st.text_input("Enter additional warehouse locations (comma separated)", value="")
custom_warehouse_locations = [loc.strip() for loc in custom_warehouse_locations_str.split(",") if loc.strip() != ""]
all_warehouse_locations = list(dict.fromkeys(base_warehouse_locations + custom_warehouse_locations))

num_warehouses = st.number_input("Number of Warehouses", min_value=1, value=1, step=1)

warehouse_data = []
for i in range(int(num_warehouses)):
    st.markdown(f"<p class='big-font'>Warehouse {i+1}</p>", unsafe_allow_html=True)
    location = st.selectbox(f"Select Location for Warehouse {i+1}", options=all_warehouse_locations, key=f"wh_location_{i}")
    
    if layout_type == "Main Regionals":
        wh_type = "MAIN"
        st.write("Warehouse Type: MAIN (Only MAIN allowed for Main Regionals layout)")
    else:
        wh_type = st.radio(f"Select Warehouse Type for Warehouse {i+1}", options=["MAIN", "FRONT"], key=f"wh_type_{i}")
    
    served_markets = st.multiselect(f"Select Market Areas served by Warehouse {i+1}", options=selected_market_areas, key=f"wh_markets_{i}")
    
    if location not in served_markets:
        st.error(f"Warehouse {i+1} location '{location}' must be included in its served market areas!")
    
    rent_pricing_method = st.radio(f"Select Rent Pricing Method for Warehouse {i+1} (Price per Year)", 
                                   options=["Fixed Rent Price", "Square Foot Rent Price"], key=f"rent_method_{i}")
    if rent_pricing_method == "Fixed Rent Price":
        rent_price = st.number_input(f"Enter Fixed Rent Price (per year, in $) for Warehouse {i+1}", 
                                     min_value=0.0, value=1000.0, step=1.0, format="%.0f", key=f"fixed_rent_{i}")
    else:
        rent_price = st.number_input(f"Enter Rent Price per Square Foot (per year, in $) for Warehouse {i+1}", 
                                     min_value=0.0, value=10.0, step=1.0, format="%.0f", key=f"sqft_rent_{i}")
    
    avg_employee_salary = st.number_input(f"Enter Average Annual Salary per Employee for Warehouse {i+1} (in $)", 
                                          min_value=0, value=50000, step=1000, format="%d", key=f"employee_salary_{i}")
    
    # Labor: number of employees with defaults:
    if wh_type == "MAIN":
        default_emp = 3 if len(served_markets) == 1 else 4
    else:
        default_emp = 2
    num_employees = st.number_input(f"Enter Number of Employees for Warehouse {i+1}", 
                                    min_value=0, value=default_emp, step=1, key=f"num_employees_{i}")
    
    # For MAIN warehouses in Main Regionals: if serving more than one market,
    # require additional inputs for each additional market (not primary)
    land_shipping_data = {}
    if wh_type == "MAIN" and layout_type == "Main Regionals" and len(served_markets) > 1:
        st.markdown(f"<p class='big-font'>Additional Land Shipping Inputs for Warehouse {i+1} (Main Regionals)</p>", unsafe_allow_html=True)
        # Assume the first market is primary; for each additional market, require:
        for add_area in served_markets[1:]:
            distance_label = f"Distance (miles) from warehouse {location} to area {add_area}"
            distance_val = st.number_input(distance_label, min_value=0.0, value=0.0, step=0.1, format="%.1f", key=f"dist_{i}_{add_area}")
            # Calculate the average order size for the area across all brands
            if add_area in market_area_data:
                avg_sizes = [params["avg_order_size"] for params in market_area_data[add_area].values()]
                area_avg_order = sum(avg_sizes)/len(avg_sizes) if avg_sizes else 0
            else:
                area_avg_order = 0
            cost_label = f"Shipping cost per average order of {area_avg_order:.0f} units per mile for area {add_area}"
            cost_val = st.number_input(cost_label, min_value=0.0, value=0.0, step=0.1, format="%.2f", key=f"cost_{i}_{add_area}")
            if cost_val == 0:
                st.error(f"Please enter a non-zero shipping cost for average order for area {add_area} in warehouse {location}.")
            land_shipping_data[add_area] = {
                "distance": distance_val,
                "cost_for_avg_order_per_mile": cost_val
            }
    
    wh_dict = {
        "location": location,
        "type": wh_type,
        "served_markets": served_markets,
        "rent_pricing_method": rent_pricing_method,
        "rent_price": rent_price,
        "avg_employee_salary": avg_employee_salary,
        "num_employees": num_employees,
    }
    if land_shipping_data:
        wh_dict["land_shipping_data"] = land_shipping_data
    
    if wh_type == "MAIN":
        lt_shipping = st.number_input(f"Enter Lead Time (days) for shipping from Israel to Warehouse {i+1} (MAIN)", 
                                      min_value=0, value=5, step=1, format="%d", key=f"lt_shipping_{i}")
        shipping_cost_40hc = st.number_input(f"Enter Shipping Cost for a 40HC container (per container, in $) from Israel to Warehouse {i+1} (MAIN)", 
                                             min_value=0, value=2000, step=1, format="%.0f", key=f"shipping_cost_40hc_{i}")
        wh_dict["lt_shipping"] = lt_shipping
        wh_dict["shipping_cost_40hc"] = shipping_cost_40hc
    elif wh_type == "FRONT":
        front_shipping_cost_40 = st.number_input(f"Enter Shipping Cost from MAIN warehouse to Warehouse {i+1} (FRONT) for a 40ft HC container (in $)", 
                                                 min_value=0, value=500, step=1, format="%.0f", key=f"front_shipping_cost_40_{i}")
        front_shipping_cost_53 = st.number_input(f"Enter Shipping Cost from MAIN warehouse to Warehouse {i+1} (FRONT) for a 53ft HC container (in $)", 
                                                 min_value=0, value=600, step=1, format="%.0f", key=f"front_shipping_cost_53_{i}")
        wh_dict["front_shipping_cost_40"] = front_shipping_cost_40
        wh_dict["front_shipping_cost_53"] = front_shipping_cost_53
        
        main_wh_options = []
        main_wh_mapping = {}
        for j, w in enumerate(warehouse_data):
            if w["type"] == "MAIN":
                option_str = f"Warehouse {j+1} - {w['location']}"
                main_wh_options.append(option_str)
                main_wh_mapping[option_str] = j
        if main_wh_options:
            serving_central = st.selectbox(f"Select the MAIN warehouse serving Warehouse {i+1} (FRONT)", options=main_wh_options, key=f"serving_central_{i}")
            wh_dict["serving_central"] = serving_central
            main_wh_index = main_wh_mapping.get(serving_central)
            if main_wh_index is not None:
                main_wh = warehouse_data[main_wh_index]
                common_markets = set(main_wh["served_markets"]).intersection(set(served_markets))
                if not common_markets:
                    st.error(f"Selected MAIN warehouse for Warehouse {i+1} does not serve any of its market areas!")
        else:
            st.error(f"No MAIN warehouse available to serve Warehouse {i+1} (FRONT). Please define a MAIN warehouse first.")
            wh_dict["serving_central"] = None
    warehouse_data.append(wh_dict)

# =============================================================================
# Additional Validation
# =============================================================================
st.markdown("<p class='subheader-font'>Validation</p>", unsafe_allow_html=True)
market_not_served = []
for market in selected_market_areas:
    served = any(market in wh["served_markets"] for wh in warehouse_data)
    if not served:
        market_not_served.append(market)
if market_not_served:
    st.error(f"The following market areas are not served by any warehouse: {', '.join(market_not_served)}")

# =============================================================================
# Helper Functions for Calculation (with Brands)
# =============================================================================

def compute_max_monthly_forecast(warehouse):
    max_monthly = 0
    for m in range(12):
        month_sum = 0
        for area in warehouse["served_markets"]:
            if area in market_area_data:
                # Sum over all brands in the area
                for brand, params in market_area_data[area].items():
                    month_sum += params["forecast_demand"][m]
        if month_sum > max_monthly:
            max_monthly = month_sum
    return max_monthly

def compute_daily_demand_sum(warehouse):
    total = 0
    for area in warehouse["served_markets"]:
        if area in market_area_data:
            for brand, params in market_area_data[area].items():
                total += params["avg_daily_demand"]
    return total

def compute_annual_demand(warehouse):
    total = 0
    for area in warehouse["served_markets"]:
        if area in market_area_data:
            for brand, params in market_area_data[area].items():
                total += sum(params["forecast_demand"])
    return total

def compute_std_sum(warehouse):
    total = 0
    for area in warehouse["served_markets"]:
        if area in market_area_data:
            for brand, params in market_area_data[area].items():
                total += params["std_daily_demand"]
    return total

def compute_safety_stock_main(warehouse, layout):
    std_sum = compute_std_sum(warehouse)
    LT = warehouse.get("lt_shipping", 0)
    safety_stock_main = std_sum * sqrt(LT) * Z_value
    if layout == "Central and Fronts":
        front_daily_demand = 0
        for wh in warehouse_data:
            if wh["type"] == "FRONT":
                for area in wh["served_markets"]:
                    if area in market_area_data:
                        for brand, params in market_area_data[area].items():
                            front_daily_demand += params["avg_daily_demand"]
        safety_stock_main += 12 * front_daily_demand
    return safety_stock_main

# =============================================================================
# Rental Cost Calculation
# =============================================================================
st.markdown("<p class='subheader-font'>Rental Cost Calculation</p>", unsafe_allow_html=True)
if st.button("Calculate Rental Costs"):
    total_rental_cost = 0.0
    for wh in warehouse_data:
        rent_method = wh["rent_pricing_method"]
        rent_price = wh["rent_price"]
        wh_type = wh["type"]
        
        if rent_method == "Fixed Rent Price":
            wh_rental_cost = rent_price
            wh_area = 0.0
        else:
            if wh_type == "MAIN":
                max_monthly = compute_max_monthly_forecast(wh)
                safety_stock_main = compute_safety_stock_main(wh, layout_type)
                total_units = max_monthly + safety_stock_main
                wh_rental_cost = rent_price * sq_ft_per_unit * overhead_factor_main * total_units
                wh_area = wh_rental_cost / rent_price
            else:
                max_monthly = compute_max_monthly_forecast(wh)
                daily_sum = compute_daily_demand_sum(wh)
                total_units = (max_monthly / 4.0) + (daily_sum * 12.0)
                wh_rental_cost = rent_price * sq_ft_per_unit * overhead_factor_front * total_units
                wh_area = wh_rental_cost / rent_price
        
        wh["rental_cost"] = wh_rental_cost
        wh["rental_area"] = wh_area
        total_rental_cost += wh_rental_cost
    
    st.subheader("Rental Cost Results")
    for i, wh in enumerate(warehouse_data):
        st.write(f"**Warehouse {i+1}** - Location: {wh['location']}")
        st.write(f"Type: {wh['type']}")
        st.write(f"Pricing Method: {wh['rent_pricing_method']}")
        st.write(f"Annual Rental Cost: ${wh['rental_cost']:.2f}")
        if wh["rent_pricing_method"] == "Square Foot Rent Price":
            st.write(f"Calculated Warehouse Area (sq ft): {wh['rental_area']:.2f}")
        st.write("---")
    st.write(f"**Total Rental Cost for All Warehouses:** ${total_rental_cost:.2f}")

# =============================================================================
# Inventory Financing Calculation (UPDATED FORMULA)
# =============================================================================
st.markdown("<p class='subheader-font'>Inventory Financing Calculation</p>", unsafe_allow_html=True)
if st.button("Calculate Inventory Financing"):
    if layout_type == "Central and Fronts":
        main_wh = next((wh for wh in warehouse_data if wh["type"] == "MAIN"), None)
        if main_wh is None:
            st.error("No MAIN warehouse found for 'Central and Fronts' layout.")
        else:
            safety_stock_main = compute_safety_stock_main(main_wh, layout_type)
            annual_demand = 0
            for area in main_wh["served_markets"]:
                if area in market_area_data:
                    for brand, params in market_area_data[area].items():
                        annual_demand += sum(params["forecast_demand"])
            avg_inventory = (annual_demand / 12.0) + safety_stock_main
            financing_cost = avg_inventory * 1.08 * (interest_rate / 100.0) * unit_cost
            total_avg_inventory = avg_inventory
            total_safety_stock = safety_stock_main
    elif layout_type == "Main Regionals":
        overall_avg_inventory = 0
        overall_safety_stock = 0
        for wh in warehouse_data:
            if wh["type"] == "MAIN":
                safety_stock_main = compute_safety_stock_main(wh, layout_type)
                annual_demand_wh = compute_annual_demand(wh)
                avg_inventory_wh = (annual_demand_wh / 12.0) + safety_stock_main
                overall_avg_inventory += avg_inventory_wh
                overall_safety_stock += safety_stock_main
        total_avg_inventory = overall_avg_inventory
        total_safety_stock = overall_safety_stock
        financing_cost = overall_avg_inventory * 1.08 * (interest_rate / 100.0) * unit_cost

    st.subheader("Inventory Financing Results")
    st.write(f"Total Safety Stock: {total_safety_stock:.2f} units")
    st.write(f"Average Inventory Level: {total_avg_inventory:.2f} units")
    st.write(f"Inventory Financing Cost (per year): ${financing_cost:.2f}")

# =============================================================================
# Shipping (Transportation) Cost Calculation
# =============================================================================
st.markdown("<p class='subheader-font'>Shipping Cost Calculation</p>", unsafe_allow_html=True)

container_capacity_40 = st.number_input(
    "Container Capacity for 40ft HC (units, default 600)",
    min_value=0,
    value=600,
    step=1,
    format="%d"
)

if st.button("Calculate Shipping Costs"):
    total_sea_shipping_cost = 0.0
    total_land_shipping_cost = 0.0

    # --- Sea Shipping Cost ---
    if layout_type in ["Central and Fronts", "Main Regionals"]:
        if layout_type == "Central and Fronts":
            main_wh = next((wh for wh in warehouse_data if wh["type"] == "MAIN"), None)
            if main_wh is None:
                st.error("No MAIN warehouse found for shipping cost calculation (Central & Fronts).")
            else:
                for area in main_wh["served_markets"]:
                    if area in market_area_data:
                        area_forecast = 0
                        for brand, params in market_area_data[area].items():
                            area_forecast += sum(params["forecast_demand"])
                        containers = area_forecast / container_capacity_40
                        total_sea_shipping_cost += containers * main_wh["shipping_cost_40hc"]
        elif layout_type == "Main Regionals":
            for wh in warehouse_data:
                if wh["type"] == "MAIN":
                    wh_sea_cost = 0
                    for area in wh["served_markets"]:
                        if area in market_area_data:
                            area_forecast = 0
                            for brand, params in market_area_data[area].items():
                                area_forecast += sum(params["forecast_demand"])
                            containers = area_forecast / container_capacity_40
                            wh_sea_cost += containers * wh["shipping_cost_40hc"]
                    total_sea_shipping_cost += wh_sea_cost

    # --- Land Shipping Cost ---
    if layout_type == "Central and Fronts":
        for wh in warehouse_data:
            if wh["type"] == "FRONT":
                warehouse_land_cost = 0
                for m in range(12):
                    monthly_forecast = 0
                    for area in wh["served_markets"]:
                        if area in market_area_data:
                            for brand, params in market_area_data[area].items():
                                monthly_forecast += params["forecast_demand"][m]
                    weekly_demand = monthly_forecast / 4.0
                    cost_40_unit = wh["front_shipping_cost_40"] / container_capacity_40
                    cost_53_unit = wh["front_shipping_cost_53"] / (container_capacity_40 * 1.37)
                    avg_cost_unit = (cost_40_unit + cost_53_unit) / 2.0
                    normalized_cost = avg_cost_unit / 0.85
                    weekly_shipping_cost = weekly_demand * normalized_cost
                    warehouse_land_cost += weekly_shipping_cost * 4
                total_land_shipping_cost += warehouse_land_cost
    elif layout_type == "Main Regionals":
        for wh in warehouse_data:
            if wh["type"] == "MAIN" and len(wh["served_markets"]) > 1:
                additional_data = wh.get("land_shipping_data", {})
                for area in wh["served_markets"][1:]:
                    if area in market_area_data:
                        if area not in additional_data or additional_data[area]["cost_for_avg_order_per_mile"] == 0:
                            st.error(f"Missing shipping cost input for average order for area {area} in warehouse {wh['location']}.")
                        else:
                            area_forecast = 0
                            for brand, params in market_area_data[area].items():
                                area_forecast += sum(params["forecast_demand"])
                            # For each brand, we can sum the annual forecast, then:
                            # Convert shipping cost to cost per unit per mile:
                            # Use the shipping cost input and divide by avg_order_size (per brand) and sum over brands.
                            area_land_cost = 0
                            for brand, params in market_area_data[area].items():
                                annual_forecast_brand = sum(params["forecast_demand"])
                                avg_size_brand = params["avg_order_size"]
                                cost_for_avg_order = additional_data[area]["cost_for_avg_order_per_mile"]
                                cost_per_unit_per_mile = cost_for_avg_order / avg_size_brand
                                distance = additional_data[area]["distance"]
                                area_land_cost += distance * cost_per_unit_per_mile * annual_forecast_brand
                            total_land_shipping_cost += area_land_cost

    total_shipping_cost = total_sea_shipping_cost + total_land_shipping_cost

    st.subheader("Shipping Cost Results")
    st.write(f"Sea Shipping Cost: ${total_sea_shipping_cost:.2f}")
    st.write(f"Land Shipping Cost: ${total_land_shipping_cost:.2f}")
    st.write(f"Total Shipping Cost (per year): ${total_shipping_cost:.2f}")

# =============================================================================
# Labor Cost Calculation
# =============================================================================
st.markdown("<p class='subheader-font'>Labor Cost Calculation</p>", unsafe_allow_html=True)
if st.button("Calculate Labor Costs"):
    total_labor_cost = 0
    for wh in warehouse_data:
        labor_cost = wh["avg_employee_salary"] * wh["num_employees"]
        wh["labor_cost"] = labor_cost
        total_labor_cost += labor_cost
    st.subheader("Labor Cost Results")
    for i, wh in enumerate(warehouse_data):
        st.write(f"**Warehouse {i+1}** - Location: {wh['location']}")
        st.write(f"Type: {wh['type']}")
        st.write(f"Number of Employees: {wh['num_employees']}")
        st.write(f"Average Annual Salary: ${wh['avg_employee_salary']}")
        st.write(f"Annual Labor Cost: ${wh['labor_cost']}")
        st.write("---")
    st.write(f"**Total Labor Cost for All Warehouses:** ${total_labor_cost}")

# =============================================================================
# Submission
# =============================================================================
if st.button("Submit Data"):
    st.write("Data submitted successfully!")
    st.write("Global Parameters:", {
        "interest_rate": f"{interest_rate} %",
        "service_level": service_level,
        "layout_type": layout_type,
        "unit_cost": f"${unit_cost}"
    })
    st.write("Market Area Data:", market_area_data)
    st.write("Warehouse Data:", warehouse_data)
