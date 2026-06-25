import streamlit as st
import pandas as pd
import io
from math import gcd
from functools import reduce

# -------------------------------------------------------------------------
# Core Mathematical Engine Logic (Strict Proportional Top-Down Layer-Locked)
# -------------------------------------------------------------------------

def lcm(a, b):
    return abs(a * b) // gcd(a, b)

def frac_denominator_approx(val, max_den=10000):
    for d in range(1, max_den):
        if abs(round(val * d) - (val * d)) < 1e-5:
            return d
    return 100

def calculate_reset_ceiling(percentages):
    denominators = []
    for p in percentages:
        if p <= 0:
            continue
        val = p / 100.0
        try:
            den = frac_denominator_approx(val)
            denominators.append(den)
        except:
            denominators.append(100)
            
    if not denominators:
        return 100
    return reduce(lcm, denominators)

def get_layer_winner(remainder_dict, weight_dict, priority_dict, labels):
    """
    Evaluates an isolated layer. Uses strict relative parent proportion accumulation
    and spends exactly 1.0 relative unit from the winner to completely avoid negative deficits.
    """
    # 1. Increment remainders cleanly using the active relative parent weights
    for k in remainder_dict.keys():
        remainder_dict[k] += (weight_dict[k] / 100.0)
        
    # 2. Select the optimal winner node based on current accumulated advantages
    winner = max(
        remainder_dict.keys(),
        key=lambda k: (
            int(remainder_dict[k] >= 1.0), 
            remainder_dict[k], 
            -priority_dict[k]
        )
    )
    
    active_score = remainder_dict[winner]
    
    # 3. Dynamic audit logger implementation using exactly 3 mathematical scenarios
    if active_score >= 1.0:
        remark = f"{labels['just_threshold']} ({active_score:.4f} >= १)"
    else:
        tied_nodes = [k for k, v in remainder_dict.items() if abs(v - active_score) < 1e-6]
        if len(tied_nodes) > 1:
            remark = f"{labels['just_tie']}: [{', '.join(tied_nodes)}] को समान अङ्क ({active_score:.4f}) देखिएकाले प्राथमिकता क्रमको आधारमा"
        else:
            sorted_rem = sorted([v for k, v in remainder_dict.items() if k != winner], reverse=True)
            if sorted_rem:
                top_others = sorted_rem[:3]
                others_str = ", ".join([f"{x:.4f}" for x in top_others])
                if len(sorted_rem) > 3:
                    others_str += ", etc."
                remark = f"{labels['just_highest_frac']}: ({active_score:.4f} > {others_str})"
            else:
                remark = f"{labels['just_highest_frac']}: ({active_score:.4f})"
                
    # 4. Pure Proportional Subtraction: Spent exactly 1.0 unit of the accumulated layer currency
    remainder_dict[winner] -= 1.0
    return winner, remark

def allocate_schedule(df_config, labels, limit_run=None, calculation_depth="Layer 4"):
    df_active = df_config.copy()
    
    ceiling = calculate_reset_ceiling(df_active['Net_Percentage'].values)
    total_iterations = ceiling if limit_run is None else min(ceiling, limit_run)
    allocations = []
    
    # --- ISOLATED INDEPENDENT MEMORY POOLS ---
    l1_keys = df_active['Level1'].unique().tolist()
    l1_remainders = {k: 0.0 for k in l1_keys}
    
    l2_remainders = {}
    l3_remainders = {}
    l4_remainders = {}
    
    # --- PROGRESSIVE LEDGER COUNTERS ---
    l1_counters = {}
    l2_counters = {}
    final_group_counters = {}

    for post_idx in range(1, total_iterations + 1):
        
        # -----------------------------------------------------------------
        # LAYER 1: Main Method Evaluation
        # -----------------------------------------------------------------
        l1_weights = df_active[['Level1', 'L1_Priority']].drop_duplicates().set_index('Level1')
        l1_pct_dict = {k: df_active[df_active['Level1'] == k]['Net_Percentage'].sum() for k in l1_keys}
        l1_prio_dict = l1_weights['L1_Priority'].to_dict()
        
        l1_winner, l1_remark = get_layer_winner(l1_remainders, l1_pct_dict, l1_prio_dict, labels)
        final_remark = l1_remark
        
        l1_counters[l1_winner] = l1_counters.get(l1_winner, 0) + 1
        current_l1_tally = l1_counters[l1_winner]
        
        # -----------------------------------------------------------------
        # LAYER 2: Sub-Method Evaluation
        # -----------------------------------------------------------------
        l2_sub = df_active[df_active['Level1'] == l1_winner]
        l2_keys = l2_sub['Level2'].unique().tolist()
        
        for k in l2_keys:
            if f"{l1_winner}->{k}" not in l2_remainders:
                l2_remainders[f"{l1_winner}->{k}"] = 0.0
                
        if calculation_depth != "Layer 1" and (len(l2_keys) > 1 or l2_keys[0] != l1_winner):
            l2_pool = {k: l2_remainders[f"{l1_winner}->{k}"] for k in l2_keys}
            l2_weights_dict = l2_sub.drop_duplicates(subset=['Level2']).set_index('Level2')['L2_Priority'].to_dict()
            
            # Use strict local relative 100% distribution inside this L1 parent
            l2_pct_dict = {k: (l2_sub[l2_sub['Level2'] == k]['percentage'].values[0]) for k in l2_keys}
            
            l2_winner, l2_remark = get_layer_winner(l2_pool, l2_pct_dict, l2_weights_dict, labels)
            final_remark = l2_remark
            
            # Save back into the active scoped memory pool
            for k in l2_keys:
                l2_remainders[f"{l1_winner}->{k}"] = l2_pool[k]
        else:
            l2_winner = l1_winner
            
        l2_path_key = f"{l1_winner}->{l2_winner}"
        l2_counters[l2_path_key] = l2_counters.get(l2_path_key, 0) + 1
        current_l2_tally = l2_counters[l2_path_key]
            
        # -----------------------------------------------------------------
        # LAYER 3: Sub-Sub-Method Evaluation
        # -----------------------------------------------------------------
        l3_sub = l2_sub[l2_sub['Level2'] == l2_winner]
        l3_keys = l3_sub['Level3'].unique().tolist()
        
        for k in l3_keys:
            if f"{l1_winner}->{l2_winner}->{k}" not in l3_remainders:
                l3_remainders[f"{l1_winner}->{l2_winner}->{k}"] = 0.0
                
        if calculation_depth not in ["Layer 1", "Layer 2"] and (len(l3_keys) > 1 or l3_keys[0] != l2_winner):
            l3_pool = {k: l3_remainders[f"{l1_winner}->{l2_winner}->{k}"] for k in l3_keys}
            l3_weights_dict = l3_sub.drop_duplicates(subset=['Level3']).set_index('Level3')['L3_Priority'].to_dict()
            
            # Use strict local relative 100% distribution inside this L2 parent
            l3_pct_dict = {k: (l3_sub[l3_sub['Level3'] == k]['percentage'].values[0]) for k in l3_keys}
            
            l3_winner, l3_remark = get_layer_winner(l3_pool, l3_pct_dict, l3_weights_dict, labels)
            final_remark = l3_remark
            
            for k in l3_keys:
                l3_remainders[f"{l1_winner}->{l2_winner}->{k}"] = l3_pool[k]
        else:
            l3_winner = l2_winner
            
        # -----------------------------------------------------------------
        # LAYER 4: Final Target Quota Evaluation
        # -----------------------------------------------------------------
        l4_sub = l3_sub[l3_sub['Level3'] == l3_winner]
        l4_keys = l4_sub['Level4'].unique().tolist()
        
        for k in l4_keys:
            if f"{l1_winner}->{l2_winner}->{l3_winner}->{k}" not in l4_remainders:
                l4_remainders[f"{l1_winner}->{l2_winner}->{l3_winner}->{k}"] = 0.0
                
        if calculation_depth == "Layer 4" and (len(l4_keys) > 1 or l4_keys[0] != l3_winner):
            l4_pool = {k: l4_remainders[f"{l1_winner}->{l2_winner}->{l3_winner}->{k}"] for k in l4_keys}
            l4_weights_dict = l4_sub.set_index('Level4')['L4_Priority'].to_dict()
            
            # Use strict local relative 100% distribution inside this L3 parent
            l4_pct_dict = {k: (l4_sub[l4_sub['Level4'] == k]['percentage'].values[0]) for k in l4_keys}
            
            l4_winner, l4_remark = get_layer_winner(l4_pool, l4_pct_dict, l4_weights_dict, labels)
            final_remark = l4_remark
            
            for k in l4_keys:
                l4_remainders[f"{l1_winner}->{l2_winner}->{l3_winner}->{k}"] = l4_pool[k]
        else:
            l4_winner = l3_winner
            
        # -----------------------------------------------------------------
        # OUTPUT TABLE COMPILATION
        # -----------------------------------------------------------------
        path_elements = [l1_winner]
        if calculation_depth != "Layer 1" and l2_winner != l1_winner:
            path_elements.append(l2_winner)
        if calculation_depth not in ["Layer 1", "Layer 2"] and l3_winner != l2_winner:
            path_elements.append(l3_winner)
        if calculation_depth == "Layer 4" and l4_winner != l3_winner:
            path_elements.append(l4_winner)
            
        full_path_str = ", ".join(path_elements)
        final_group_counters[full_path_str] = final_group_counters.get(full_path_str, 0) + 1
        
        allocations.append({
            labels['out_post_no']: post_idx,
            labels['col_path_header']: full_path_str,
            labels['out_l1_tally']: current_l1_tally,
            labels['out_l2_tally']: current_l2_tally,
            labels['out_cum_tally']: final_group_counters[full_path_str],
            labels['out_justification']: final_remark
        })
        
    return ceiling, pd.DataFrame(allocations)

# -------------------------------------------------------------------------
# Bilingual Translation Reference Dictionary Matrix
# -------------------------------------------------------------------------

LANG_DATA = {
    'English': {
        'title': "⚖️ Smart Top-Down Post Allocation Builder System",
        'subtitle': "Construct your organization's legal breakdown hierarchically using relative parent percentages.",
        'build_header': "🛠️ Dynamic Organizational Structure Model",
        'add_l1': "➕ Add Layer 1 Category",
        'clear_tree': "🗑️ Clear Structure Setup",
        'l1_label': "Category Name (Layer 1)",
        'l1_prio': "L1 Priority",
        'l1_pct': "Share of Total Posts (%)",
        'add_l2': "➕ Add Layer 2 Sub-Category",
        'l2_label': "Sub-Category Name (Layer 2)",
        'l2_prio': "L2 Priority",
        'l2_pct': "Share of this Category (%)",
        'add_l3': "➕ Add Layer 3 Sub-Sub-Category",
        'l3_label': "Sub-Sub-Category Name (Layer 3)",
        'l3_prio': "L3 Priority",
        'l3_pct': "Share of this Sub-Category (%)",
        'add_l4': "➕ Add Layer 4 Target Group",
        'l4_label': "Target Quota Group Name (Layer 4)",
        'l4_prio': "L4 Priority",
        'l4_pct': "Share of this Sub-Sub-Category (%)",
        'live_view': "### Live Compiled View of Settings (Calculated Net Share)",
        'col_path_header': "📋 Category Path / पदपूर्ति विवरण (Levels)",
        'col_pct_header': "📈 Calculated Global Net Share (%) / खुद प्रतिशत",
        'reset_mem': "🗑️ Clear Memory Structure",
        'warn_l1': "⚠️ Layer 1 total categories sum up to {}%. It must equal exactly 100%.",
        'warn_l2': "⚠️ Sub-categories under '{}' sum up to {}%. It must equal exactly 100%.",
        'warn_l3': "⚠️ Sub-sub-categories under '{} -> {}' sum up to {}%. It must equal exactly 100%.",
        'warn_l4': "⚠️ Target groups under '{} -> {} -> {}' sum up to {}%. It must equal exactly 100%.",
        'success_sum': "✅ All custom dynamic layers balance perfectly to 100% of their respective parent nodes.",
        'exec_header': "⚙️ Roster Engine Execution Hub",
        'magic_num_metric': "Calculated Reset Ceiling (Magic Pattern Number)",
        'limit_label': "🎯 Generation Limit Selector: How many posts do you want to calculate right now?",
        'limit_hint': "(Safely caps your active browser render to avoid computer freezing parameters)",
        'mode_label': "🛠️ Target Calculation Mode Method:",
        'mode_opt_full': "Full Schedule (Run through Deepest Groups)",
        'mode_opt_level': "Isolate and Calculate up to Selected Level Only",
        'depth_select_label': "Choose Target Calculation Depth Layer:",
        'export_label': "Choose Reference Document Output Format:",
        'process_btn': "🚀 Execute Pattern Generator Loop",
        'calc_success': "Execution Successful! True Reset Ceiling is {} posts. Generated requested {} sequence rows.",
        'dl_xlsx': "📥 Download Distribution Reference Roster (.xlsx)",
        'dl_txt': "📥 Download Distribution Reference Roster (.txt)",
        'new_cat': "New Layer",
        'new_sub': "New Sub-Layer",
        'new_subsub': "New Sub-Sub-Layer",
        'new_grp': "Group",
        'out_post_no': "Vacant Post No.",
        'out_l1_tally': "Layer 1 Count",
        'out_l2_tally': "Layer 2 Count",
        'out_cum_tally': "Cumulative Target Count",
        'out_justification': "Mathematical Justification",
        'just_threshold': "Threshold Win: Share balance",
        'just_highest_frac': "Highest Fraction",
        'just_tie': "On Priority Basis",
        'confirm_del_title': "⚠️ Are you sure you want to delete this level branch?",
        'confirm_del_msg': "Deleting a parent item will automatically wipe out all nested sub-parent levels and groups beneath it!",
        'btn_yes_del': "Yes, Delete Branch"
    },
    'नेपाली': {
        'title': "⚖️ पदपूर्ति पदसंख्या निर्धारण प्रणाली",
        'subtitle': "ऐन वा बिनियममा भएको पदपूर्ति तालिका अनुसार प्रतिशत ढाँचा इन्ट्रि गर्नुहोस्।",
        'build_header': "🛠️ पदपूर्ति विधिको वहु-तह संरचना",
        'add_l1': "➕ पहिलो  तहको विधि थप्नुहोस् (तह १)",
        'clear_tree': "🗑️ सम्पूर्ण संरचना हटाउनुहोस्",
        'l1_label': "पहिलो  तहको विधि (तह १)",
        'l1_prio': "प्रतिशत प्राथमिकता",
        'l1_pct': "कूल दरबन्दीमा यसको हिस्सा (%)",
        'add_l2': "➕ यस तह भन्तर पर्ने विधि थप्नुहोस् (तह २)",
        'l2_label': "उप-विधि (तह २)",
        'l2_prio': "तह २ प्राथमिकता",
        'l2_pct': "यस अन्तर्गतको सापेक्षित हिस्सा (%)",
        'add_l3': "➕ उप-उप-तहका विधि थप्नुहोस् (तह ३)",
        'l3_label': "उप-उप-विधि (तह ३)",
        'l3_prio': "तह ३ प्राथमिकता",
        'l3_pct': "यस अन्तर्गतको सापेक्षित हिस्सा (%)",
        'add_l4': "➕ उप-उप-विधि भित्रको कोटा थप्नुहोस् (तह ४)",
        'l4_label': "कोटा/समूहको नाम (तह ४)",
        'l4_prio': "तह ४ प्राथमिकता",
        'l4_pct': "यस अन्तर्गतको सापेक्षित हिस्सा (%)",
        'live_view': "### हाल प्रविष्ट गरिएको सेटिङको विवरण (प्रणालीद्वारा गणना गरिएको खुद राष्ट्रिय हिस्सा)",
        'col_path_header': "📋 पदपूर्ति विवरण (Levels)",
        'col_pct_header': "📈 खुद प्रतिशत (%)",
        'reset_mem': "🗑️ प्रविष्ट डेटा र मेमोरी सफा गर्नुहोस्",
        'warn_l1': "⚠️  तह १ का मुख्य विधिहरूको योगफल {}% देखिएको छ। यो ठीक १००% हुन अनिवार्य छ।",
        'warn_l2': "⚠️ '{}' भित्रका उप-श्रेणी विधिहरूको योगफल {}% देखिएको छ। यो ठीक १००% हुन अनिवार्य छ।",
        'warn_l3': "⚠️ '{} -> {}' भित्रका कोटा/समूहहरूको योगफल {}% देखिएको छ। यो ठीक १००% हुन अनिवार्य छ।",
        'warn_l4': "⚠️ '{} -> {} -> {}' भित्रका समूहहरूको योगफल {}% देखिएको छ। यो ठीक १००% हुन अनिवार्य छ।",
        'success_sum': "✅ सबै विधिहरू आ-आफ्नो हिस्सासँग १००% मिलान भएका छन्। अब, तालिका प्रशोधन गर्नका लागि तयार छ।",
        'exec_header': "⚙️ नतिजा प्रशोधन तथा प्रतिशत विवरण तयारी",
        'magic_num_metric': "पुनँ सुरु हुने उच्चतम सीमा चक्र (म्याजिक नम्बर)",
        'limit_label': "🎯 गणना सीमा: तपाईँ हाल कतिवटा खाली पदको क्रमिक तालिका निकाल्न चाहनुहुन्छ?",
        'limit_hint': "(यदि गणितीय चक्रको उच्चतम सीमा लाखौँमा निस्कियो भने कम्प्युटर ह्याङ हुनबाट जोगाउँछ)",
        'mode_label': "🛠️ तालिकीकरण छनोट विधि:",
        'mode_opt_full': "पूर्ण तालिका (अन्तिम तहसम्मै निकाल्ने)",
        'mode_opt_level': "प्रयोगकर्ताले रोजेको निश्चित तहसम्मको मात्र तालिका निकाल्ने",
        'depth_select_label': "कुन तहको आधारमा क्रमिक तालिका निकाल्ने हो, छनोट गर्नुहोस्:",
        'export_label': "Export गर्ने फाइलको ढाँचा रोज्नुहोस्:",
        'process_btn': "🚀 प्रतिशत निर्धारण चक्र र पदक्रम तालिका गणना गर्नुहोस्",
        'calc_success': "प्रशोधन सफल भयो! वास्तविक गन्तव्य चक्र सीमा {} रहेको छ। अनुरोध गरिएका {} वटा पदहरूको तालिका तयार भयो।",
        'dl_xlsx': "📥 तयार भएको पदक्रम तालिका डाउनलोड गर्नुहोस् (.xlsx)",
        'dl_txt': "📥 तयार भएको पदक्रम तालिका डाउनलोड गर्नुहोस् (.txt)",
        'new_cat': "नयाँ तह",
        'new_sub': "नयाँ उप-तह",
        'new_subsub': "नयाँ उप-उप-तह",
        'new_grp': "समूह",
        'out_post_no': "विज्ञापन/माग पद क्र.सं.",
        'out_l1_tally': "तह १ को सङ्ख्या",
        'out_l2_tally': "तह २ को सङ्ख्या",
        'out_cum_tally': "कोटा अन्तर्गतको कुल संख्या",
        'out_justification': "बाँडफाँडको आधार / गणितीय पुष्टि",
        'just_threshold': "न्यूनतम सीमा: सञ्चित मौज्दात",
        'just_highest_frac': "उच्चतम् दशमलव अंश",
        'just_tie': "प्राथमिकताको आधारमा",
        'confirm_del_title': "⚠️ के तपाईं यो विधि शाखा हटाउन निश्चित हुनुहुन्छ?",
        'confirm_del_msg': "यो मातृ विधि हटाउँदा यस अन्तर्गत रहेका सम्पूर्ण उप-विधि, उप-उप-विधि र कोठाहरू स्वतः मेटिनेछन्!",
        'btn_yes_del': "हो, शाखा हटाउनुहोस्"
    }
}

# -------------------------------------------------------------------------
# Screen Layout Configuration
# -------------------------------------------------------------------------
st.set_page_config(page_title="Post Allocation System", layout="wide")

header_left, header_right = st.columns([4, 1])
with header_right:
    selected_lang = st.selectbox("🌐 Language / भाषा:", ["English", "नेपाली"], label_visibility="collapsed")

L = LANG_DATA[selected_lang]

with header_left:
    st.title(L['title'])
    st.write(L['subtitle'])

if 'tree_structure' not in st.session_state:
    st.session_state.tree_structure = []
if 'delete_confirm_node' not in st.session_state:
    st.session_state.delete_confirm_node = None

# -------------------------------------------------------------------------
# Confirmation Dialog Panel
# -------------------------------------------------------------------------
if st.session_state.delete_confirm_node is not None:
    with st.container(border=True):
        st.warning(f"### {L['confirm_del_title']}")
        st.write(L['confirm_del_msg'])
        
        target_node = st.session_state.delete_confirm_node
        st.info(f"📍 Targeting: {target_node['type'].upper()} -> **{target_node['name']}**")
        
        btn_c1, btn_c2 = st.columns([1, 4])
        with btn_c1:
            if st.button(L['btn_yes_del'], type="primary", key="confirm_delete_execute_btn"):
                t = target_node
                if t['type'] == 'l1':
                    st.session_state.tree_structure.pop(t['i'])
                elif t['type'] == 'l2':
                    st.session_state.tree_structure[t['i']]['sub_categories'].pop(t['j'])
                elif t['type'] == 'l3':
                    st.session_state.tree_structure[t['i']]['sub_categories'][t['j']]['sub_sub_categories'].pop(t['k'])
                elif t['type'] == 'l4':
                    st.session_state.tree_structure[t['i']]['sub_categories'][t['j']]['sub_sub_categories'][t['k']]['target_groups'].pop(t['m'])
                
                st.session_state.delete_confirm_node = None
                st.rerun()
        with btn_c2:
            if st.button("Cancel / रद्द गर्नुहोस्", type="secondary", key="cancel_delete_btn"):
                st.session_state.delete_confirm_node = None
                st.rerun()
    st.write("---")

# -------------------------------------------------------------------------
# Form Builder Interface Layout
# -------------------------------------------------------------------------
col_action1, col_action2 = st.columns([2.2, 4])
with col_action1:
    if st.button(L['add_l1'], type="primary"):
        st.session_state.tree_structure.append({
            "name": f"{L['new_cat']} {len(st.session_state.tree_structure) + 1}",
            "priority": 1, "percentage": 100.0, "sub_categories": []
        })
        st.rerun()
with col_action2:
    if st.session_state.tree_structure:
        if st.button(L['clear_tree']):
            st.session_state.tree_structure = []
            st.rerun()

for i, l1_cat in enumerate(st.session_state.tree_structure):
    with st.container(border=True):
        c1, c2, c3, c4, c5 = st.columns([2.2, 0.9, 1.1, 1.1, 0.5])
        with c1:
            l1_cat['name'] = st.text_input(f"🔹 {L['l1_label']} #{i+1}", value=l1_cat['name'], key=f"l1_n_{i}")
        with c2:
            l1_cat['priority'] = st.number_input(f"{L['l1_prio']}", min_value=1, value=l1_cat['priority'], key=f"l1_p_{i}")
        with c3:
            l1_cat['percentage'] = st.number_input(L['l1_pct'], min_value=0.0, max_value=100.0, value=l1_cat['percentage'], format="%.2f", key=f"l1_sh_{i}")
        with c4:
            st.markdown("<div style='padding-top:24px;'></div>", unsafe_allow_html=True)
            if st.button(L['add_l2'], key=f"add_l2_{i}"):
                l1_cat['sub_categories'].append({
                    "name": f"{L['new_sub']} {len(l1_cat['sub_categories']) + 1}",
                    "priority": 1, "percentage": 100.0, "sub_sub_categories": []
                })
                st.rerun()
        with c5:
            st.markdown("<div style='padding-top:24px;'></div>", unsafe_allow_html=True)
            if st.button("🗑️", key=f"del_l1_{i}"):
                st.session_state.delete_confirm_node = {"type": "l1", "i": i, "name": l1_cat['name']}
                st.rerun()
        
        for j, l2_cat in enumerate(l1_cat['sub_categories']):
            l2_space, l2_block = st.columns([0.06, 0.94])
            with l2_block:
                with st.container(border=True):
                    sc1, sc2, sc3, sc4, sc5 = st.columns([2.2, 0.9, 1.1, 1.1, 0.5])
                    with sc1:
                        l2_cat['name'] = st.text_input(f"🔸 {L['l2_label']} #{j+1}", value=l2_cat['name'], key=f"l2_n_{i}_{j}")
                    with sc2:
                        l2_cat['priority'] = st.number_input(f"{L['l2_prio']}", min_value=1, value=l2_cat['priority'], key=f"l2_p_{i}_{j}")
                    with sc3:
                        l2_cat['percentage'] = st.number_input(L['l2_pct'], min_value=0.0, max_value=100.0, value=l2_cat['percentage'], format="%.2f", key=f"l2_sh_{i}_{j}")
                    with sc4:
                        st.markdown("<div style='padding-top:24px;'></div>", unsafe_allow_html=True)
                        if st.button(L['add_l3'], key=f"add_l3_{i}_{j}"):
                            l2_cat['sub_sub_categories'].append({
                                "name": f"{L['new_subsub']} {len(l2_cat['sub_sub_categories']) + 1}",
                                "priority": 1, "percentage": 100.0, "target_groups": []
                            })
                            st.rerun()
                    with sc5:
                        st.markdown("<div style='padding-top:24px;'></div>", unsafe_allow_html=True)
                        if st.button("🗑️", key=f"del_l2_{i}_{j}"):
                            st.session_state.delete_confirm_node = {"type": "l2", "i": i, "j": j, "name": l2_cat['name']}
                            st.rerun()
                    
                    for k, l3_cat in enumerate(l2_cat['sub_sub_categories']):
                        l3_space, l3_block = st.columns([0.06, 0.94])
                        with l3_block:
                            with st.container(border=True):
                                ssc1, ssc2, ssc3, ssc4, ssc5 = st.columns([2.2, 0.9, 1.1, 1.1, 0.5])
                                with ssc1:
                                    l3_cat['name'] = st.text_input(f"🔺 {L['l3_label']} #{k+1}", value=l3_cat['name'], key=f"l3_n_{i}_{j}_{k}")
                                with ssc2:
                                    l3_cat['priority'] = st.number_input(f"{L['l3_prio']}", min_value=1, value=l3_cat['priority'], key=f"l3_p_{i}_{j}_{k}")
                                with ssc3:
                                    l3_cat['percentage'] = st.number_input(L['l3_pct'], min_value=0.0, max_value=100.0, value=l3_cat['percentage'], format="%.2f", key=f"l3_sh_{i}_{j}_{k}")
                                with ssc4:
                                    st.markdown("<div style='padding-top:24px;'></div>", unsafe_allow_html=True)
                                    if st.button(L['add_l4'], key=f"add_l4_{i}_{j}_{k}"):
                                        l3_cat['target_groups'].append({
                                            "name": f"{L['new_grp']} {len(l3_cat['target_groups']) + 1}",
                                            "priority": 1, "percentage": 100.0
                                        })
                                        st.rerun()
                                with ssc5:
                                    st.markdown("<div style='padding-top:24px;'></div>", unsafe_allow_html=True)
                                    if st.button("🗑️", key=f"del_l3_{i}_{j}_{k}"):
                                        st.session_state.delete_confirm_node = {"type": "l3", "i": i, "j": j, "k": k, "name": l3_cat['name']}
                                        st.rerun()
                                        
                                for m, l4_cat in enumerate(l3_cat['target_groups']):
                                    l4_space, l4_block = st.columns([0.06, 0.94])
                                    with l4_block:
                                        col_m_name, col_m_prio, col_m_pct, col_m_del = st.columns([2.2, 0.9, 1.1, 0.5])
                                        with col_m_name:
                                            l4_cat['name'] = st.text_input(f"📍 {L['l4_label']} #{m+1}", value=l4_cat['name'], key=f"l4_n_{i}_{j}_{k}_{m}")
                                        with col_m_prio:
                                            l4_cat['priority'] = st.number_input(f"{L['l4_prio']} #{m+1}", min_value=1, value=l4_cat['priority'], key=f"l4_p_{i}_{j}_{k}_{m}")
                                        with col_m_pct:
                                            l4_cat['percentage'] = st.number_input(L['l4_pct'], min_value=0.0, max_value=100.0, value=l4_cat['percentage'], format="%.4f", key=f"l4_sh_{i}_{j}_{k}_{m}")
                                        with col_m_del:
                                            st.markdown("<div style='padding-top:24px;'></div>", unsafe_allow_html=True)
                                            if st.button("🗑️", key=f"del_l4_{i}_{j}_{k}_{m}"):
                                                st.session_state.delete_confirm_node = {"type": "l4", "i": i, "j": j, "k": k, "m": m, "name": l4_cat['name']}
                                                st.rerun()

# -------------------------------------------------------------------------
# Compile Structural Tree Mapping
# -------------------------------------------------------------------------
flat_rows = []
validation_errors = []
df_input = None

if st.session_state.tree_structure:
    l1_total_pct = sum([c['percentage'] for c in st.session_state.tree_structure])
    if abs(l1_total_pct - 100.0) > 1e-4:
        validation_errors.append(L['warn_l1'].format(f"{l1_total_pct:.2f}"))
        
    for l1 in st.session_state.tree_structure:
        if not l1['sub_categories']:
            flat_rows.append({"Level1": l1['name'].strip(), "L1_Priority": l1['priority'], "Level2": l1['name'].strip(), "L2_Priority": 1, "Level3": l1['name'].strip(), "L3_Priority": 1, "Level4": l1['name'].strip(), "L4_Priority": 1, "percentage": l1['percentage'], "Net_Percentage": l1['percentage']})
            continue
            
        l2_total_pct = sum([sc['percentage'] for sc in l1['sub_categories']])
        if abs(l2_total_pct - 100.0) > 1e-4:
            validation_errors.append(L['warn_l2'].format(l1['name'], f"{l2_total_pct:.2f}"))
            
        for l2 in l1['sub_categories']:
            if not l2['sub_sub_categories']:
                net_share = (l1['percentage'] / 100.0) * l2['percentage']
                flat_rows.append({"Level1": l1['name'].strip(), "L1_Priority": l1['priority'], "Level2": l2['name'].strip(), "L2_Priority": l2['priority'], "Level3": l2['name'].strip(), "L3_Priority": 1, "Level4": l2['name'].strip(), "L4_Priority": 1, "percentage": l2['percentage'], "Net_Percentage": net_share})
                continue
                
            l3_total_pct = sum([ssc['percentage'] for ssc in l2['sub_sub_categories']])
            if abs(l3_total_pct - 100.0) > 1e-4:
                validation_errors.append(L['warn_l3'].format(l1['name'], l2['name'], f"{l3_total_pct:.2f}"))
                
            for l3 in l2['sub_sub_categories']:
                if not l3['target_groups']:
                    net_share = (l1['percentage'] / 100.0) * (l2['percentage'] / 100.0) * l3['percentage']
                    flat_rows.append({"Level1": l1['name'].strip(), "L1_Priority": l1['priority'], "Level2": l2['name'].strip(), "L2_Priority": l2['priority'], "Level3": l3['name'].strip(), "L3_Priority": l3['priority'], "Level4": l3['name'].strip(), "L4_Priority": 1, "percentage": l3['percentage'], "Net_Percentage": net_share})
                    continue
                    
                l4_total_pct = sum([tg['percentage'] for tg in l3['target_groups']])
                if abs(l4_total_pct - 100.0) > 1e-4:
                    validation_errors.append(L['warn_l4'].format(l1['name'], l2['name'], l3['name'], f"{l4_total_pct:.2f}"))
                    
                for tg in l3['target_groups']:
                    net_share = (l1['percentage'] / 100.0) * (l2['percentage'] / 100.0) * (l3['percentage'] / 100.0) * tg['percentage']
                    flat_rows.append({"Level1": l1['name'].strip(), "L1_Priority": l1['priority'], "Level2": l2['name'].strip(), "L2_Priority": l2['priority'], "Level3": l3['name'].strip(), "L3_Priority": l3['priority'], "Level4": tg['name'].strip(), "L4_Priority": tg['priority'], "percentage": tg['percentage'], "Net_Percentage": net_share})

if flat_rows:
    df_built = pd.DataFrame(flat_rows)
    st.write("---")
    st.write(L['live_view'])
    
    preview_summary_list = []
    for idx, r in df_built.iterrows():
        levels_pushed = [r['Level1']]
        if r['Level2'] != r['Level1']:
            levels_pushed.append(r['Level2'])
        if r['Level3'] != r['Level2']:
            levels_pushed.append(r['Level3'])
        if r['Level4'] != r['Level3']:
            levels_pushed.append(r['Level4'])
            
        comma_path_string = ", ".join(levels_pushed)
        preview_summary_list.append({
            L['col_path_header']: comma_path_string,
            L['col_pct_header']: f"{r['Net_Percentage']:.4f}%"
        })
        
    df_tidy_preview = pd.DataFrame(preview_summary_list)
    st.dataframe(df_tidy_preview, width="stretch")
    
    if validation_errors:
        for err in validation_errors:
            st.warning(err)
    else:
        st.success(L['success_sum'])
        df_input = df_built
        
    if st.button(L['reset_mem']):
        st.session_state.tree_structure = []
        st.rerun()

# -------------------------------------------------------------------------
# Execution Controls Panel
# -------------------------------------------------------------------------
if df_input is not None and not df_input.empty:
    st.markdown("---")
    st.subheader(L['exec_header'])
    
    run_mode_choice = st.radio(L['mode_label'], [L['mode_opt_full'], L['mode_opt_level']])
    
    target_depth = "Layer 4"
    if run_mode_choice == L['mode_opt_level']:
        target_depth = st.selectbox(L['depth_select_label'], ["Layer 1", "Layer 2", "Layer 3", "Layer 4"])
    
    df_temp_group = df_input.copy()
    if target_depth == "Layer 1":
        df_temp_group = df_temp_group.groupby(['Level1', 'L1_Priority'], as_index=False)['Net_Percentage'].sum()
    elif target_depth == "Layer 2":
        df_temp_group = df_temp_group.groupby(['Level1', 'L1_Priority', 'Level2', 'L2_Priority'], as_index=False)['Net_Percentage'].sum()
    elif target_depth == "Layer 3":
        df_temp_group = df_temp_group.groupby(['Level1', 'L1_Priority', 'Level2', 'L2_Priority', 'Level3', 'L3_Priority'], as_index=False)['Net_Percentage'].sum()
        
    calculated_ceiling = calculate_reset_ceiling(df_temp_group['Net_Percentage'].values)
    
    st.metric(label=L['magic_num_metric'], value=f"🎯 {calculated_ceiling:,}")
    
    st.caption(L['limit_hint'])
    slider_max = min(calculated_ceiling, 5000) if calculated_ceiling > 10 else 100
    run_limit = st.slider(
        label=L['limit_label'],
        min_value=10,
        max_value=int(slider_max),
        value=int(min(slider_max, 200)),
        step=10
    )
    
    export_format = st.radio(L['export_label'], ["Excel Workbook (.xlsx)", "Tabular Text (.txt)"])
    
    if st.button(L['process_btn'], type="primary"):
        with st.spinner("Processing allocation map sequence roster..."):
            try:
                calc_ceiling, df_final = allocate_schedule(
                    df_input, L, 
                    limit_run=run_limit, 
                    calculation_depth=target_depth
                )
                st.success(L['calc_success'].format(calc_ceiling, len(df_final)))
                st.dataframe(df_final, width="stretch")
                
                if "Excel" in export_format:
                    out_io = io.BytesIO()
                    with pd.ExcelWriter(out_io, engine='openpyxl') as wr:
                        df_final.to_excel(wr, index=False, sheet_name='Fulfillment_Roster')
                    st.download_button(
                        label=L['dl_xlsx'], data=out_io.getvalue(),
                        file_name="calculated_distribution_schedule.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    txt_io = io.StringIO()
                    df_final.to_string(txt_io, index=False)
                    st.download_button(
                        label=L['dl_txt'], data=txt_io.getvalue(),
                        file_name="calculated_distribution_schedule.txt",
                        mime="text/plain"
                    )
            except Exception as e:
                st.error(f"Engine fault: {str(e)}")
