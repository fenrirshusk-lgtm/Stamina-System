import streamlit as st
import math

# ----- Data Tables -----
EP_COST_TABLE = [1, 1, 2, 3, 4, 5, 7, 9, 11, 14, 17, 20, 23, 26]
CONTROL_REDUCTION_TABLE = [i * 0.5 for i in range(14)]
BUFF_DEBUFF_TABLE = [i * 3 for i in range(19)]
ENDURANCE_TO_MAX_EP = [20 + i * 10 for i in range(14)]

# ----- Session State Initialization -----
if "current_ep" not in st.session_state:
    st.session_state.current_ep = 70
if "turn_count" not in st.session_state:
    st.session_state.turn_count = 1

st.title("TTRPG Stamina Calculator")

def stat_slider_with_inactive(label, min_val, max_val, default_val, allow_inactive=True):
    col1, col2 = st.sidebar.columns([4,1])
    with col1:
        val = st.slider(label, min_val, max_val, default_val)
    inactive = False
    if allow_inactive:
        with col2:
            inactive = st.checkbox("Inactive", key=f"inactive_{label}")
    return (val, inactive)

# ----- Sidebar Inputs -----
endurance = st.sidebar.slider("Endurance", 0, 13, 5)

power1, power1_inactive = stat_slider_with_inactive("Power Use 1", 0, 13, 4)
power2, power2_inactive = stat_slider_with_inactive("Power Use 2", 0, 13, 2)
range_stat, range_inactive = stat_slider_with_inactive("Range", 0, 13, 3)
control, control_inactive = stat_slider_with_inactive("Control", 0, 13, 4)
mobility_stat, mobility_inactive = stat_slider_with_inactive("Mobility", 0, 13, 3)
buff_debuff = st.sidebar.slider("Stat Buff/Debuff", 0, 18, 0)

extra_costs = st.sidebar.number_input("Extra Costs (flat EP)", min_value=0.0, value=0.0, step=0.5)
upkeep = st.sidebar.checkbox("Upkeep (halve Power Use 1 EP cost)", value=False)
deactivated_regen = st.sidebar.checkbox("Deactivated Regen (regen every turn)", value=False)

# ----- Max EP -----
max_ep = ENDURANCE_TO_MAX_EP[endurance]

# ----- Reset Button -----
if st.sidebar.button("Reset"):
    st.session_state.turn_count = 0
    st.session_state.current_ep = max_ep

# ----- Cost/Reduction Functions -----
def get_control_reduction(stat, inactive):
    return 0 if inactive else CONTROL_REDUCTION_TABLE[stat]

def get_buff_debuff(stat):
    return BUFF_DEBUFF_TABLE[stat]

def get_ep_cost(stat, inactive, apply_upkeep=False):
    if inactive:
        return 0
    ep = EP_COST_TABLE[stat]
    if apply_upkeep:
        ep /= 2
    return ep

# ----- Individual EP Costs -----
ep_power1 = get_ep_cost(power1, power1_inactive, upkeep)
ep_power2 = get_ep_cost(power2, power2_inactive)
ep_range = get_ep_cost(range_stat, range_inactive)
buff_debuff_cost = get_buff_debuff(buff_debuff)
control_reduction = get_control_reduction(control, control_inactive)

# ----- Mobility Cost Calculation -----
if mobility_inactive:
    ep_mobility = 0
else:
    raw_mobility_cost = EP_COST_TABLE[mobility_stat] - control_reduction
    raw_mobility_cost = max(raw_mobility_cost, 0)
    raw_mobility_cost /= 2

    if raw_mobility_cost % 1 in [0.25, 0.75]:
        ep_mobility = math.ceil(raw_mobility_cost * 2) / 2
    else:
        ep_mobility = raw_mobility_cost

    if ep_mobility > 0:
        ep_mobility = max(1, ep_mobility)

# ----- Total Cost Calculation -----
raw_cost = (
    ep_power1 +
    ep_power2 +
    ep_range +
    ep_mobility +
    buff_debuff_cost +
    extra_costs -
    control_reduction
)

# Rounding logic
if raw_cost % 1 in [0.25, 0.75]:
    total_cost = math.ceil(raw_cost * 2) / 2
else:
    total_cost = round(raw_cost)

# Enforce final min value of 1 (if greater than 0)
if total_cost > 0:
    total_cost = max(1, total_cost)
else:
    total_cost = 0

# ----- EP Handling -----
st.sidebar.header("Turn Management")
starting_ep = st.sidebar.number_input("Current EP", min_value=0, value=st.session_state.current_ep, step=1)

regen_turn = deactivated_regen or (st.session_state.turn_count % 2 == 0)
regen_amount = int(round(max_ep * 0.10)) if regen_turn else 0

if st.sidebar.button("Next Turn"):
    new_ep = st.session_state.current_ep + regen_amount
    new_ep = min(new_ep, max_ep)
    new_ep -= total_cost
    new_ep = max(0, new_ep)
    st.session_state.current_ep = new_ep
    st.session_state.turn_count += 1

remaining_ep = st.session_state.current_ep - total_cost

# ----- Output -----
st.subheader("EP Breakdown")

st.write(f"**Max EP** (Endurance {endurance}): {max_ep}")
st.write(f"**Current EP** (Turn {st.session_state.turn_count}): {st.session_state.current_ep}")

st.write(f"**Power Use 1 Cost** (Inactive: {power1_inactive}): {ep_power1}")
st.write(f"**Power Use 2 Cost** (Inactive: {power2_inactive}): {ep_power2}")
st.write(f"**Range Cost** (Inactive: {range_inactive}): {ep_range}")
st.write(f"**Mobility Cost** (Inactive: {mobility_inactive}): {ep_mobility}")
st.write(f"**Buff/Debuff Cost**: {buff_debuff_cost}")
st.write(f"**Control Reduction** (Inactive: {control_inactive}): {control_reduction}")
st.write(f"**Extra Costs**: {extra_costs}")

st.write(f"**Total EP Cost (after rounding, min 1 applied last)**: {total_cost}")
st.write(f"**Stamina Regen this turn:** {regen_amount}")
st.write(f"**Remaining EP After Action**: {remaining_ep}")

# Mobility Value display (for movement, not EP)
mobility_value = 0 if mobility_inactive else math.ceil((power1 - control_reduction) / 2)
st.write(f"**Mobility Value (rounded up):** {mobility_value}")

# EP Warning
if remaining_ep < 0:
    st.error("⚠️ You do not have enough EP for this action!")
else:
    st.success("✅ EP is sufficient for this action.")
