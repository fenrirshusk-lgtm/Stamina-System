import streamlit as st

# Lookup tables
EP_COST_TABLE = {
    0: 1, 1: 1, 2: 2, 3: 3, 4: 4,
    5: 5, 6: 7, 7: 9, 8: 11, 9: 14,
    10: 17, 11: 20, 12: 23, 13: 26
}

CONTROL_REDUCTION_TABLE = {
    i: i * 0.5 for i in range(14)
}

ENDURANCE_TO_MAX_EP = {
    i: 20 + i * 10 for i in range(14)
}

# UI
st.title("TTRPG Stamina Calculator")

st.sidebar.header("Input Stats")
endurance = st.sidebar.slider("Endurance Stat", 0, 13, 5)
power = st.sidebar.slider("Power Stat", 0, 13, 4)
range_stat = st.sidebar.slider("Range Stat", 0, 13, 3)
control = st.sidebar.slider("Control Stat", 0, 13, 4)
num_uses = st.sidebar.number_input("Number of Uses", min_value=1, value=1, step=1)

# Lookup values
max_ep = ENDURANCE_TO_MAX_EP[endurance]
ep_power = EP_COST_TABLE[power]
ep_range = EP_COST_TABLE[range_stat]
control_reduction = CONTROL_REDUCTION_TABLE[control]

# Mobility calculation
mobility_value = max((power - control_reduction) / 2, 0)

# EP cost calculation
base_total = (ep_power * num_uses) + ep_range
reduced_total = max(base_total - control_reduction, 0)
remaining_ep = max_ep - reduced_total

# Output
st.subheader("Results")
st.write(f"**Max EP** (Endurance {endurance}): {max_ep}")
st.write(f"**EP per Use** (Power {power}): {ep_power}")
st.write(f"**Range EP Cost** (Range {range_stat}): {ep_range}")
st.write(f"**Control Reduction** (Control {control}): {control_reduction}")
st.write(f"**Mobility Value**: {mobility_value:.2f}")
st.write(f"**Total EP Cost**: {reduced_total:.2f}")
st.write(f"**Remaining EP**: {remaining_ep:.2f}")

if remaining_ep < 0:
    st.error("⚠️ Warning: You don't have enough stamina for this!")
else:
    st.success("✅ You have enough stamina!")

# Bar chart
st.subheader("EP Usage Overview")
st.bar_chart({
    "EP": {
        "Used": reduced_total if remaining_ep > 0 else max_ep,
        "Remaining": remaining_ep if remaining_ep > 0 else 0
    }
})
