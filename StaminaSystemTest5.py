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

st.title("TTRPG Stamina Calculator")

def stat_slider_with_inactive(label, min_val, max_val, default_val):
    """Return (value, inactive) tuple from slider + checkbox"""
    col1, col2 = st.sidebar.columns([4,1])
    with col1:
        val = st.slider(label, min_val, max_val, default_val)
    with col2:
        inactive = st.checkbox("Inactive", key=f"inactive_{label}")
    return (val, inactive)

# ----- Sidebar Inputs with Inactive Toggles -----
endurance, endurance_inactive = stat_slider_with_inactive("Endurance", 0, 13, 5)
power1, power1_inactive = stat_slider_with_inactive("Power Use 1", 0, 13, 4)
range_stat, range_inactive = stat_slider_with_inactive("Range", 0, 13, 3)
control, control_inactive = stat_slider_with_inactive("Control", 0, 13, 4)
mobility, mobility_inactive = stat_slider_with_inactive("Mobility", 0, 13, 3)
buff_debuff, buff_debuff_inactive = stat_slider_with_inactive("Stat Buff/Debuff", 0, 18, 0)

# ----- Upkeep Toggle -----
upkeep = st.sidebar.checkbox("Upkeep (halve Power Use 1 EP cost)", value=False)

# ----- Calculate max EP from Endurance -----
max_ep = 0 if endurance_inactive else ENDURANCE_TO_MAX_EP[endurance]

# ----- Calculate EP costs and reductions -----
def get_ep_cost(stat, inactive):
    return 0 if inactive else EP_COST_TABLE[stat]

def get_control_reduction(stat, inactive):
    return 0 if inactive else CONTROL_REDUCTION_TABLE[stat]

def get_buff_debuff(stat, inactive):
    return 0 if inactive else BUFF_DEBUFF_TABLE[stat]

ep_power1 = get_ep_cost(power1, power1_inactive)
if upkeep and not power1_inactive:
    ep_power1 /= 2

ep_range = get_ep_cost(range_stat, range_inactive)

control_reduction = get_control_reduction(control, control_inactive)

buff_debuff_cost = get_buff_debuff(buff_debuff, buff_debuff_inactive)

ep_mobility = get_ep_cost(mobility, mobility_inactive)

# ----- Raw total cost -----
raw_cost = ep_power1 + ep_range + buff_debuff_cost + ep_mobility - control_reduction

# If Endurance inactive, no stamina to spend => total cost = 0
if endurance_inactive:
    raw_cost = 0

# ----- Rounding rules -----
if raw_cost % 1 in [0.25, 0.75]:
    total_cost = math.ceil(raw_cost * 2) / 2
else:
    total_cost = round(raw_cost)

# ----- Minimum cost enforcement -----
# Only enforce if raw_cost > 0, else 0 allowed
if raw_cost > 0:
    total_cost = max(1, total_cost)
else:
    total_cost = 0

# ----- Current EP Management -----
st.sidebar.header("Turn Management")
starting_ep = st.sidebar.number_input("Current EP", min_value=0, value=st.session_state.current_ep, step=1)

if st.sidebar.button("Next Turn"):
    # Update current EP to remaining EP
    new_ep = starting_ep - total_cost
    st.session_state.current_ep = max(new_ep, 0)

remaining_ep = st.session_state.current_ep - total_cost

# ----- Output -----
st.subheader("EP Breakdown")

st.write(f"**Max EP** (Endurance {endurance}{' - Inactive' if endurance_inactive else ''}): {max_ep}")
st.write(f"**Current EP**: {st.session_state.current_ep}")

st.write(f"**Power Use 1 Cost** ({"Inactive" if power1_inactive else power1}): {ep_power1}")
st.write(f"**Range Cost** ({"Inactive" if range_inactive else range_stat}): {ep_range}")
st.write(f"**Mobility Cost** ({"Inactive" if mobility_inactive else mobility}): {ep_mobility}")
st.write(f"**Buff/Debuff Cost** ({"Inactive" if buff_debuff_inactive else buff_debuff}): {buff_debuff_cost}")
st.write(f"**Control Reduction** ({"Inactive" if control_inactive else control}): {control_reduction}")

st.write(f"**Total EP Cost (after rounding & min 1 rule)**: {total_cost}")
st.write(f"**Remaining EP After Action**: {remaining_ep}")

# Mobility displayed also as separate stat value (round up)
mobility_value = 0 if mobility_inactive else math.ceil((power1 - control_reduction) / 2)
st.write(f"**Mobility Value (rounded up):** {mobility_value}")

# EP warning
if remaining_ep < 0:
    st.error("⚠️ You do not have enough EP for this action!")
else:
    st.success("✅ EP is sufficient for this action.")

# ----- Visualization -----
st.subheader("EP Usage Chart")
st.bar_chart({
    "EP": {
        "Used": total_cost if remaining_ep >= 0 else st.session_state.current_ep,
        "Remaining": max(remaining_ep, 0)
    }
})
