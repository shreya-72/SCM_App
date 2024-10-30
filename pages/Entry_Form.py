import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd


# Display Title and Description
st.title("Vendor Management Portal")
st.markdown("Enter the details of the new vendor below.")

# Establishing a Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)
                     
                    

# Fetch existing vendors data
existing_data = conn.read(worksheet="Forecasted_data", usecols=list(range(28)), ttl=5)
existing_data = existing_data.dropna(how="all")

# st.dataframe(existing_data)

# List of Business Types and Products
BUSINESS_TYPES = [
    "Manufacturer",
    "Distributor",
    "Wholesaler",
    "Retailer",
    "Service Provider",
]
PRODUCTS = [
    "Electronics",
    "Apparel",
    "Groceries",
    "Software",
    "Other",
]

# Onboarding New Vendor Form
with st.form(key="vendor_form"):
    item_code = st.text_input(label="Item Code*")
    item_description = st.selectbox("Item Description*", options=BUSINESS_TYPES, index=None)
    # products = st.multiselect("Products Offered", options=PRODUCTS)
    # company_name = st.text_input(label="Part No")
    years_in_business = st.slider("Years in Business", 0, 50, 5)
    onboarding_date = st.date_input(label="Onboarding Date")
    additional_info = st.text_area(label="Additional Notes")

    # Mark mandatory fields
    st.markdown("**required*")

    submit_button = st.form_submit_button(label="Submit Vendor Details")

    # If the submit button is pressed
    if submit_button:
        # Check if all mandatory fields are filled
        if not item_code or not item_description:
            st.warning("Ensure all mandatory fields are filled.")
            st.stop()
        # elif existing_data["CompanyName"].str.contains(company_name).any():
        #     st.warning("A vendor with this company name already exists.")
        #     st.stop()
        else:
            # Create a new row of vendor data
            vendor_data = pd.DataFrame(
                [
                    {
                        "Item Code": item_code,
                        "Item Description": item_description,
                        # "Products": ", ".join(products),
                        # "YearsInBusiness": years_in_business,
                        # "OnboardingDate": onboarding_date.strftime("%Y-%m-%d"),
                        # "AdditionalInfo": additional_info,
                    }
                ]
            )

            # Add the new vendor data to the existing data
            updated_df = pd.concat([existing_data, vendor_data], ignore_index=True)

            # Update Google Sheets with the new vendor data
            conn.update(worksheet="Forecasted_data", data=updated_df)

            st.success("Vendor details successfully submitted!")