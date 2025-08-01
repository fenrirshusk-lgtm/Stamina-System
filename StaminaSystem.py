import streamlit as st

# Mapping tables
ENDURANCE_TO_MAX_EP = {
    i: 20 + i * 10 for i in range(14)
}

POWER_TO_EP_COST = {
    0: 1, 1: 1, 2: 2, 3: 3, 4: 4,
    5: 5, 6: 7, 7: 9, 8: 11, 9: 14,
    10: 17, 11: 20, 12: 23, 13: 26
}

# Streamlit UI
st.title("TTRPG Stamina Calculator")

st.sidebar.header("Input Stats")

endurance = st.sidebar.slider("Endurance Stat", 0, 13, 5)
power = st.sidebar.slider("Power Use Stat", 0, 13, 4)
num_uses = st.sidebar.number_input("Number of Uses", min_value=1, value=1, step=1)

# Calculation
max_ep = ENDURANCE_TO_MAX_EP[endurance]
ep_per_use = POWER_TO_EP_COST[power]
total_cost = ep_per_use * num_uses
remaining_ep = max_ep - total_cost

# Output
st.subheader("Results")
st.write(f"**Max EP** (Endurance {endurance}): {max_ep}")
st.write(f"**EP Cost per Use** (Power {power}): {ep_per_use}")
st.write(f"**Total EP Cost** ({num_uses} uses): {total_cost}")
st.write(f"**Remaining EP**: {remaining_ep}")

if remaining_ep < 0:
    st.error("⚠️ Warning: You don't have enough stamina for this!")
else:
    st.success("✅ You have enough stamina!")

# Optional: Bar chart
st.subheader("EP Usage Overview")
st.bar_chart({
    "EP": {
        "Used": total_cost if remaining_ep > 0 else max_ep,
        "Remaining": remaining_ep if remaining_ep > 0 else 0
    }
})
