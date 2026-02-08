<?php
/*
Plugin Name: Tapvaani AI - Ultimate Astrology Engine
Description: Professional Kundli SVG, AM/PM, Place, Lucky Number/Color and AI Analysis.
Version: 70.0
Author: Ranjeet Sharma (Tapvaani.com)
*/

if (!defined('ABSPATH')) exit;

// 1. Settings Menu
add_action('admin_menu', function() {
    add_options_page('Tapvaani AI Config', 'Tapvaani AI', 'manage_options', 'tapvaani-config', 'tap_settings_ui');
});

function tap_settings_ui() {
    if (isset($_POST['save_tap'])) {
        update_option('tap_gemini_key', sanitize_text_field($_POST['g_key']));
        update_option('tap_vercel_url', esc_url_raw(untrailingslashit($_POST['v_url'])));
        echo '<div class="updated"><p>Settings Saved! ✅</p></div>';
    }
    ?>
    <div class="wrap">
        <h1>🔱 Tapvaani AI Dashboard</h1>
        <form method="post">
            <input type="password" name="g_key" value="<?php echo esc_attr(get_option('tap_gemini_key')); ?>" placeholder="Gemini Key" style="width:400px;"><br><br>
            <input type="text" name="v_url" value="<?php echo esc_url(get_option('tap_vercel_url')); ?>" placeholder="Vercel URL" style="width:400px;"><br><br>
            <?php submit_button('Save Settings'); ?>
        </form>
    </div>
    <?php
}

// 2. SVG Kundli Drawer
function draw_tap_kundli_svg($lagna_no, $planets) {
    $house_rashis = [];
    for ($i = 1; $i <= 12; $i++) { $house_rashis[$i] = ($lagna_no + $i - 2) % 12 + 1; }
    $house_planets = array_fill(1, 12, []);
    foreach ($planets as $name => $p_data) { $house_planets[$p_data['house']][] = substr($name, 0, 2); }
    ob_start(); ?>
    <svg width="320" height="320" viewBox="0 0 300 300" style="background:#fff; border:2px solid #ff9933; margin:20px auto; display:block; border-radius:10px;">
        <rect width="300" height="300" fill="none" stroke="#ff9933" stroke-width="4"/>
        <line x1="0" y1="0" x2="300" y2="300" stroke="#ff9933" stroke-width="2"/>
        <line x1="300" y1="0" x2="0" y2="300" stroke="#ff9933" stroke-width="2"/>
        <polygon points="150,0 300,150 150,300 0,150" fill="none" stroke="#ff9933" stroke-width="2"/>
        <?php 
        $coords = [1=>[150,85,150,60],2=>[75,50,75,30],3=>[50,85,30,85],4=>[75,150,75,130],5=>[50,235,30,235],6=>[75,270,75,290],7=>[150,235,150,260],8=>[225,270,225,290],9=>[270,235,290,235],10=>[225,150,225,130],11=>[270,85,290,85],12=>[225,50,225,30]];
        foreach ($coords as $h => $pos) {
            echo '<text x="'.$pos[2].'" y="'.$pos[3].'" font-size="12" fill="#d35400" text-anchor="middle">'.$house_rashis[$h].'</text>';
            $p_text = implode(' ', $house_planets[$h]);
            echo '<text x="'.$pos[0].'" y="'.$pos[1].'" font-size="14" font-weight="bold" fill="#333" text-anchor="middle">'.$p_text.'</text>';
        } ?>
    </svg>
    <?php return ob_get_clean();
}

// 3. AJAX Logic
add_action('wp_ajax_get_tapvaani_full_report', 'tap_ajax_handler');
add_action('wp_ajax_nopriv_get_tapvaani_full_report', 'tap_ajax_handler');

function tap_ajax_handler() {
    $name = sanitize_text_field($_POST['u_name']);
    $dob = sanitize_text_field($_POST['u_dob']);
    $h = intval($_POST['u_hours']);
    $m = intval($_POST['u_mins']);
    $ampm = sanitize_text_field($_POST['u_ampm']);
    $place = sanitize_text_field($_POST['u_place']);

    if ($ampm == 'PM' && $h < 12) $h += 12;
    if ($ampm == 'AM' && $h == 12) $h = 0;
    $tob = sprintf('%02d:%02d', $h, $m);

    $v_url = get_option('tap_vercel_url');
    $res = wp_remote_get("{$v_url}/calculate?dob={$dob}&tob={$tob}", array('timeout'=>30));
    $data = json_decode(wp_remote_retrieve_body($res), true);
    if ($data['status'] !== 'success') wp_send_json_error($data['message']);

    $chart = $data['data'];
    $g_key = get_option('tap_gemini_key');
    $prompt = "Expert Vedic Astrologer. User: $name, Moon Rashi: {$chart['moon_rashi']}, Lagna: {$chart['lagna_name']}. Write daily horoscope in Hindi with headings: स्वास्थ्य, करियर, धन, शुभ अंक, शुभ रंग, आज का मंत्र.";

    $ai_res = wp_remote_post("https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=$g_key", array(
        'headers' => array('Content-Type' => 'application/json'),
        'body' => json_encode(array("contents" => array(array("parts" => array(array("text" => $prompt))))))
    ));
    $ai_data = json_decode(wp_remote_retrieve_body($ai_res), true);
    $text = $ai_data['candidates'][0]['content']['parts'][0]['text'] ?? 'AI Error';

    ob_start(); ?>
    <div style="background:#fff; border:2px solid #ff9933; padding:25px; border-radius:20px; font-family:sans-serif;">
        <h2 style="text-align:center; color:#ff9933;">🔱 Tapvaani Astrology Report</h2>
        <div style="display:flex; justify-content:space-between; background:#fff9f0; padding:15px; border-radius:10px; font-size:14px; border:1px solid #ffe0b3;">
            <div><b>Name:</b> <?php echo $name; ?><br><b>Place:</b> <?php echo $place; ?></div>
            <div style="text-align:right;"><b>Date:</b> <?php echo $dob; ?><br><b>Time:</b> <?php echo "$h:$m $ampm"; ?></div>
        </div>
        <div style="text-align:center;">
            <?php echo draw_tap_kundli_svg($chart['lagna'], $chart['planets']); ?>
            <p style="font-weight:bold; color:#d35400;">लग्न: <?php echo $chart['lagna_name']; ?> | राशि: <?php echo $chart['moon_rashi']; ?></p>
        </div>
        <div style="margin-top:20px; line-height:1.6;">
            <?php echo preg_replace('/\*\*(.*?)\*\*/', '<b style="color:#e67e22; display:block; margin-top:10px;">$1</b>', nl2br(esc_html($text))); ?>
        </div>
        <div style="text-align:center; margin-top:20px;"><button onclick="window.print();" style="padding:10px 20px; background:#333; color:#fff; border-radius:50px; cursor:pointer;">Print PDF</button></div>
    </div>
    <?php wp_send_json_success(ob_get_clean());
}

// 4. Shortcode UI
add_shortcode('tapvaani_rashifal', function() {
    ob_start(); ?>
    <div style="max-width:500px; margin:auto; background:#fff; padding:30px; border-radius:30px; box-shadow:0 15px 50px rgba(0,0,0,0.1); border-top:10px solid #ff9933;">
        <h2 style="text-align:center;">🔱 Tapvaani Accurate Astro</h2>
        <form id="tap-pro-form">
            <input type="text" id="u_name" placeholder="Name" required style="width:100%; padding:15px; margin-bottom:10px; border-radius:10px; border:1px solid #ddd;">
            <input type="text" id="u_place" placeholder="Birth Place (City)" required style="width:100%; padding:15px; margin-bottom:10px; border-radius:10px; border:1px solid #ddd;">
            <input type="date" id="u_dob" required style="width:100%; padding:15px; margin-bottom:10px; border-radius:10px; border:1px solid #ddd;">
            <div style="display:flex; gap:10px; margin-bottom:20px;">
                <select id="u_hours" style="flex:1; padding:15px; border-radius:10px; border:1px solid #ddd;"><?php for($i=1;$i<=12;$i++) echo "<option>$i</option>"; ?></select>
                <select id="u_mins" style="flex:1; padding:15px; border-radius:10px; border:1px solid #ddd;"><?php for($i=0;$i<=59;$i++) echo sprintf("<option>%02d</option>",$i,$i); ?></select>
                <select id="u_ampm" style="flex:1; padding:15px; border-radius:10px; border:1px solid #ddd;"><option>AM</option><option>PM</option></select>
            </div>
            <button type="submit" style="width:100%; padding:20px; background:linear-gradient(to right, #ff9933, #ff5500); color:#fff; border:none; border-radius:15px; font-weight:bold; cursor:pointer;">देखें भविष्य ➔</button>
        </form>
        <div id="tap-loading" style="display:none; text-align:center; margin-top:20px;">⏳ गणना जारी है...</div>
        <div id="tap-report-area" style="margin-top:30px;"></div>
    </div>
    <script>
    jQuery(document).ready(function($) {
        $('#tap-pro-form').on('submit', function(e) {
            e.preventDefault();
            $('#tap-loading').show(); $('#tap-report-area').hide();
            $.ajax({
                url: '<?php echo admin_url('admin-ajax.php'); ?>',
                type: 'POST',
                data: {
                    action: 'get_tapvaani_full_report',
                    u_name: $('#u_name').val(), u_place: $('#u_place').val(), u_dob: $('#u_dob').val(),
                    u_hours: $('#u_hours').val(), u_mins: $('#u_mins').val(), u_ampm: $('#u_ampm').val()
                },
                success: function(res) {
                    $('#tap-loading').hide();
                    if(res.success) { $('#tap-report-area').html(res.data).fadeIn(); }
                    else { alert(res.data); }
                }
            });
        });
    });
    </script>
    <?php return ob_get_clean();
});
