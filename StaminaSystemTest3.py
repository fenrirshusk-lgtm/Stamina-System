import streamlit as st
import math

# ----- Data Tables -----
EP_COST_TABLE = [1, 1, 2, 3, 4, 5, 7, 9, 11, 14, 17, 20, 23, 26]
CONTROL_REDUCTION_TABLE = [i * 0.5 for i in range(14)]
BUFF_DEBUFF_TABLE = [i * 3 for i in range(19)]
ENDURANCE_TO_MAX_EP = [20 + i * 10 for i in range(14)]

# ----- Session State Initialization -----
if "current_ep" not in st.session_state:
    st.session_state.current_ep = 70  # default starting value

# ----- Title -----
st.title("TTRPG Stamina Calculator")

# ----- Sidebar Inputs -----
st.sidebar.header("Stats")

endurance = st.sidebar.slider("Endurance", 0, 13, 5)
power1 = st.sidebar.slider("Power Use 1", 0, 13, 4)
power2 = st.sidebar.slider("Power Use 2", 0, 13, 0)
range_stat = st.sidebar.slider("Range", 0, 13, 3)
control = st.sidebar.slider("Control", 0, 13, 4)
buff_debuff = st.sidebar.slider("Stat Buff/Debuff", 0, 18, 0)

# ----- Control and Buff/Debuff Effects -----
control_reduction = CONTROL_REDUCTION_TABLE[control]
buff_debuff_cost = BUFF_DEBUFF_TABLE[buff_debuff]

# ----- Upkeep Toggle -----
upkeep = st.sidebar.checkbox("Upkeep (halve Power Use 1 EP cost)", value=False)

# ----- Calculated EP Costs -----
ep_power1 = EP_COST_TABLE[power1] / 2 if upkeep else EP_COST_TABLE[power1]
ep_power2 = EP_COST_TABLE[power2]
ep_range = EP_COST_TABLE[range_stat]

raw_cost = ep_power1 + ep_power2 + ep_range + buff_debuff_cost - control_reduction
# Rounding rules
if raw_cost % 1 in [0.25, 0.75]:
    total_cost = math.ceil(raw_cost * 2) / 2
else:
    total_cost = round(raw_cost)

# Enforce minimum cost of 1
total_cost = max(1, total_cost)

# ----- Mobility -----
mobility = math.ceil((power1 - control_reduction) / 2)
mobility_input = st.sidebar.number_input("Mobility (editable)", min_value=0, value=mobility)

# ----- Current EP Management -----
st.sidebar.header("Turn Management")
starting_ep = st.sidebar.number_input("Current EP", min_value=0, value=st.session_state.current_ep, step=1)
if st.sidebar.button("Next Turn"):
    st.session_state.current_ep = starting_ep

# ----- Max EP -----
max_ep = ENDURANCE_TO_MAX_EP[endurance]
remaining_ep = starting_ep - total_cost

# ----- Output -----
st.subheader("EP Breakdown")
st.write(f"**Max EP** (Endurance {endurance}): {max_ep}")
st.write(f"**Current EP**: {starting_ep}")
st.write(f"**Power Use 1 Cost**: {ep_power1}")
st.write(f"**Power Use 2 Cost**: {ep_power2}")
st.write(f"**Range Cost**: {ep_range}")
st.write(f"**Buff/Debuff Cost**: {buff_debuff_cost}")
st.write(f"**Control Reduction**: {control_reduction}")
st.write(f"**Total EP Cost (after rounding & min 1)**: {total_cost}")
st.write(f"**Remaining EP After Action**: {remaining_ep}")
st.write(f"**Mobility**: {mobility_input}")

# EP warning
if remaining_ep < 0:
    st.error("⚠️ You do not have enough EP for this action!")
else:
    st.success("✅ EP is sufficient for this action.")

# ----- Visualization -----
st.subheader("EP Usage Chart")
st.bar_chart({
    "EP": {
        "Used": total_cost if remaining_ep > 0 else starting_ep,
        "Remaining": max(remaining_ep, 0)
    }
})
