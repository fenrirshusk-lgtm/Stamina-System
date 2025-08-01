import streamlit as st
import math

# ----- Data Tables -----
EP_COST_TABLE = [1, 1, 2, 3, 4, 5, 7, 9, 11, 14, 17, 20, 23, 26]
CONTROL_REDUCTION_TABLE = [i * 0.5 for i in range(14)]
BUFF_DEBUFF_TABLE = [i * 3 for i in range(19)]
ENDURANCE_TO_MAX_EP = [20 + i * 10 for i in range(14)]

# ----- Session State Initialization -----
if "current_ep" not in st.session_state:
    st.session_state.current_ep = 70  # default starting EP
if "turn_count" not in st.session_state:
    st.session_state.turn_count = 1  # start at turn 1

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
endurance = st.sidebar.slider("Endurance", 0, 13, 5)  # no inactive toggle

power1, power1_inactive = stat_slider_with_inactive("Power Use 1", 0, 13, 4)
range_stat, range_inactive = stat_slider_with_inactive("Range", 0, 13, 3)
control, control_inactive = stat_slider_with_inactive("Control", 0, 13, 4)
mobility, mobility_inactive = stat_slider_with_inactive("Mobility", 0, 13, 3)
buff_debuff = st.sidebar.slider("Stat Buff/Debuff", 0, 18, 0)  # no inactive toggle

# Extra Costs input
extra_costs = st.sidebar.number_input("Extra Costs (flat EP)", min_value=0.0, value=0.0, step=0.5)

# Upkeep toggle
upkeep = st.sidebar.checkbox("Upkeep (halve Power Use 1 EP cost)", value=False)

# Regen toggles
deactivated_regen = st.sidebar.checkbox("Deactivated Regen (regen every turn)", value=False)

# ----- Calculate max EP from Endurance -----
max_ep = ENDURANCE_TO_MAX_EP[endurance]

# Reset button
if st.sidebar.button("Reset"):
    st.session_state.turn_count = 0
    st.session_state.current_ep = max_ep

# ----- Calculate EP costs and reductions -----
def get_ep_cost(stat, inactive):
    return 0 if inactive else EP_COST_TABLE[stat]

def get_control_reduction(stat, inactive):
    return 0 if inactive else CONTROL_REDUCTION_TABLE[stat]

def get_buff_debuff(stat):
    return BUFF_DEBUFF_TABLE[stat]

ep_power1 = get_ep_cost(power1, power1_inactive)
if upkeep and not power1_inactive:
    ep_power1 /= 2

ep_range = get_ep_cost(range_stat, range_inactive)

control_reduction = get_control_reduction(control, control_inactive)

buff_debuff_cost = get_buff_debuff(buff_debuff)

ep_mobility = 0 if mobility_inactive else EP_COST_TABLE[mobility]

# ----- Raw total cost -----
raw_cost = ep_power1 + ep_range + buff_debuff_cost + ep_mobility - control_reduction + extra_costs

# ----- Rounding rules -----
if raw_cost % 1 in [0.25, 0.75]:
    total_cost = math.ceil(raw_cost * 2) / 2
else:
    total_cost = round(raw_cost)

# ----- Minimum cost enforcement -----
if raw_cost > 0:
    total_cost = max(1, total_cost)
else:
    total_cost = 0

# ----- Current EP Management -----
st.sidebar.header("Turn Management")
starting_ep = st.sidebar.number_input("Current EP", min_value=0, value=st.session_state.current_ep, step=1)

# Calculate regeneration amount
regen_turn = False
if deactivated_regen:
    regen_turn = True
else:
    # regen every second turn
    regen_turn = (st.session_state.turn_count % 2 == 0)

regen_amount = int(round(max_ep * 0.10)) if regen_turn else 0

if st.sidebar.button("Next Turn"):
    # Apply regen first
    new_ep = st.session_state.current_ep + regen_amount
    if new_ep > max_ep:
        new_ep = max_ep
    # Subtract EP cost
    new_ep -= total_cost
    if new_ep < 0:
        new_ep = 0
    st.session_state.current_ep = new_ep
    st.session_state.turn_count += 1

remaining_ep = st.session_state.current_ep - total_cost

# ----- Output -----
st.subheader("EP Breakdown")

st.write(f"**Max EP** (Endurance {endurance}): {max_ep}")
st.write(f"**Current EP** (Turn {st.session_state.turn_count}): {st.session_state.current_ep}")

st.write(f"**Power Use 1 Cost** ({"Inactive" if power1_inactive else power1}): {ep_power1}")
st.write(f"**Range Cost** ({"Inactive" if range_inactive else range_stat}): {ep_range}")
st.write(f"**Mobility Cost** ({"Inactive" if mobility_inactive else mobility}): {ep_mobility}")
st.write(f"**Buff/Debuff Cost**: {buff_debuff_cost}")
st.write(f"**Control Reduction** ({"Inactive" if control_inactive else control}): {control_reduction}")
st.write(f"**Extra Costs**: {extra_costs}")

st.write(f"**Total EP Cost (after rounding & min 1 rule)**: {total_cost}")

st.write(f"**Stamina Regen this turn:** {regen_amount}")

st.write(f"**Remaining EP After Action**: {remaining_ep}")

# Mobility displayed also as separate stat value (round up)
mobility_value = 0 if mobility_inactive else math.ceil((power1 - control_reduction) / 2)
st.write(f"**Mobility Value (rounded up):** {mobility_value}")

# EP warning
if remaining_ep < 0:
    st.error("⚠️ You do not have enough EP for this action!")
else:
    st.success("✅ EP is sufficient for this action.")
