const $ = require('./node_modules/jquery');
const S = require('./node_modules/smoothie');
const convert = require('./node_modules/color-convert');
const Noty = require('./node_modules/noty')

const delay = 1000;
const notify_delay = delay*4;

var dev_notify_stack = [];
var db_writing_notify = false;

var ts_stack = [];

var datatypes = [];
var datl = 0;
var charts = [];
var chtl = 0;

var devices = [];
var devl = 0;
var device_styles = [];

function generate_style(n, total){
    var h = 360*(n/total);
    var rgb = convert.hsl.rgb(h, 100, 50);
    var hex = convert.rgb.hex(rgb);
    var r = rgb[0]; var g = rgb[1]; var b = rgb[2];
    var style = {color_hex: hex,
                 strokeStyle: 'rgb('+r+','+g+','+b+')', 
                 fillStyle: 'rgba('+r+','+g+','+b+','+'0.3)', 
                 lineWidth: 3};
    return style;
}

function generate_styles(){
    for (var d = 0; d < devl; d++){
        var ds = generate_style(d, devl);
        device_styles.push(ds);
    }
}

function colorify_device_names(){
    for (var d = 0; d < devl; d++){
        var dev = devices[d];
        var devname = document.getElementById('device_name_'+dev);
        devname.style.color = '#'+device_styles[d].color_hex
    }
}

function generate_dev_notify_stack() {
    for (var d = 0; d < devl; d++){
        dev_notify_stack.push(false);
    }
}


$.getJSON('/api/control', function(d){
    datatypes = d['datatypes'];
    devices = d['visible_devices'];
    datl = datatypes.length;
    devl = devices.length;
    // notify
    if (d['is_db_writing_enabled'] == false) { db_writing_notify = true }
    generate_dev_notify_stack();
    // styles
    generate_styles();
    colorify_device_names();
    for (var i = 0; i < datl; i++){
	    var chart = new S.SmoothieChart();
	    chart.streamTo(document.getElementById(datatypes[i]), delay);
	    for (var d = 0; d < devl; d++){
	        var ts = new S.TimeSeries();
	        ts_stack.push(ts);
            //add time series and style
	        chart.addTimeSeries(ts, device_styles[d]);
	}
	charts.push(chart);
    }
    chtl = charts.length;
});

function update_data() {
    $.getJSON('/api/data', function(jd){
        var cd = jd['current'];
        //console.log(cd);
        for (var c = 0; c < chtl; c++){
            var dt = datatypes[c];
            chart = charts[c];
            for (var d = 0; d < devl; d++){
                var device = devices[d];
                ts = ts_stack[c*devl+d];
                var devdat = cd[device];
                if (devdat['is_fresh']){
                    ts.append(new Date().getTime(), devdat[dt]);
                } else {
                    dev_notify_stack[d] = true;
                }
            }
        }
    });
}

function notify_no_data_from_device(devname){
    n = new Noty({
        type: 'warning',
        layout: 'topRight',
        text: 'No data from device <b>' + devname + '</b>'
    });
    n.setTimeout(notify_delay);
    n.show()
}

function notify_db_is_not_writing(){
    n = new Noty({
        type: 'warning',
        layout: 'topRight',
        text: 'Data is <b>NOT</b> writing into the database'
    });
    n.setTimeout(notify_delay);
    n.show();
}

function notify_daemon() {
    for (var d = 0; d < devl; d++){
        if (dev_notify_stack[d]){
            notify_no_data_from_device(devices[d]);
            dev_notify_stack[d] = false;
        }
    }
    if (db_writing_notify) {
        notify_db_is_not_writing();
        db_writing_notify = false;
    }
}

setInterval(update_data, delay);
setInterval(notify_daemon, notify_delay)
