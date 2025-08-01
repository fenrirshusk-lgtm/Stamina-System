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

# ----- Title -----
st.title("Anthesis EP Calculator")

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
upkeep1 = st.sidebar.checkbox("Upkeep for Power Use 1 (halve cost)", value=False)
upkeep2 = st.sidebar.checkbox("Upkeep for Power Use 2 (halve cost)", value=False)
deactivated_regen = st.sidebar.checkbox("Deactivated Regen (regen every turn)", value=False)

# ----- Max EP -----
max_ep = ENDURANCE_TO_MAX_EP[endurance]

# ----- Reset Button -----
if st.sidebar.button("Reset"):
    st.session_state.turn_count = 0
    st.session_state.current_ep = max_ep

# ----- Control Reduction & Buffs -----
control_reduction = 0 if control_inactive else CONTROL_REDUCTION_TABLE[control]
buff_debuff_cost = BUFF_DEBUFF_TABLE[buff_debuff]

# ----- Function to calculate EP cost per stat -----
def compute_stat_cost(stat_val, inactive, apply_upkeep=False):
    if inactive:
        return 0
    cost = EP_COST_TABLE[stat_val]
    if apply_upkeep:
        cost /= 2
    cost -= control_reduction
    cost = max(cost, 0)

    remainder = cost % 1
    if remainder in [0.25, 0.75]:
        cost = math.ceil(cost * 2) / 2

    return max(cost, 1) if cost > 0 else 0

# ----- EP Costs -----
ep_power1 = compute_stat_cost(power1, power1_inactive, apply_upkeep=upkeep1)
ep_power2 = compute_stat_cost(power2, power2_inactive, apply_upkeep=upkeep2)
ep_range = compute_stat_cost(range_stat, range_inactive)

# ----- Mobility Cost -----
if mobility_inactive:
    ep_mobility = 0
else:
    base = EP_COST_TABLE[mobility_stat] - control_reduction
    base = max(base, 0) / 2
    ep_mobility = int(round(base))
    ep_mobility = max(ep_mobility, 1) if ep_mobility > 0 else 0

# ----- Total Cost Calculation -----
raw_total = ep_power1 + ep_power2 + ep_range + ep_mobility + buff_debuff_cost + extra_costs

remainder = raw_total % 1
if remainder in [0.25, 0.75]:
    total_cost = math.ceil(raw_total * 2) / 2
else:
    total_cost = raw_total

if total_cost > 0:
    total_cost = max(total_cost, 1)

# ----- Turn Management -----
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

st.write(f"**Power Use 1 Cost** (Inactive: {power1_inactive}, Upkeep: {upkeep1}): {ep_power1}")
st.write(f"**Power Use 2 Cost** (Inactive: {power2_inactive}, Upkeep: {upkeep2}): {ep_power2}")
st.write(f"**Range Cost** (Inactive: {range_inactive}): {ep_range}")
st.write(f"**Mobility Cost** (Inactive: {mobility_inactive}): {ep_mobility}")
st.write(f"**Buff/Debuff Cost**: {buff_debuff_cost}")
st.write(f"**Control Reduction** (Inactive: {control_inactive}): {control_reduction}")
st.write(f"**Extra Costs**: {extra_costs}")

st.write(f"**Total EP Cost (after rounding rules)**: {total_cost}")
st.write(f"**Stamina Regen this turn:** {regen_amount}")
st.write(f"**Remaining EP After Action**: {remaining_ep}")

if remaining_ep < 0:
    st.error("⚠️ You do not have enough EP for this action!")
else:
    st.success("✅ EP is sufficient for this action.")
