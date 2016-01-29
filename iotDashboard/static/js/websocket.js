var mydata = Array();
function drawVisualization() {

    var data = new google.visualization.DataTable();
    
    data.addColumn('datetime', 'Time of Day');
    data.addColumn('number', 'Light in Lux');
    
    data.addRows(
        mydata
    );
    
    
    new google.visualization.LineChart(document.getElementById('visualization')).
      draw(data, {curveType: "function",
                  width: 500, height: 400,
                  vAxis: {maxValue: 0.1}}
          );
}
google.setOnLoadCallback(drawVisualization);

feed = (function() {
    var socket = null;
    //var ellog = document.getElementById('log');
    var wsuri = "ws://" + window.location.hostname + ":8000/ws";
    var el = $('#log');
    return {
        connect: function ()
        {
            if ("WebSocket" in window) {
                socket = new WebSocket(wsuri);
            } else if ("MozWebSocket" in window) {
                socket = new MozWebSocket(wsuri);
            } else {
                console.log("Browser does not support WebSocket!");
            }
            if (socket) {
                socket.onopen = function () {
                    console.log("Connected to " + wsuri);
                    socket.send('hello');
                }

                socket.onclose = function (e) {
                    console.log("Connection closed (wasClean = " + e.wasClean + ", code = " + e.code + ", reason = '" + e.reason + "')");
                    socket = null;
                }

                socket.onmessage = function(e) {
                    var d = new Date();
                    var result = JSON.parse(JSON.parse(e.data));
                    console.log(result);
                    if(result.status==0){
                        if($("#"+result.method).length==0){
                            $('#content').prepend("<h2>Logs: "+result.method+"</h2>") 
                            $("#content").append("<div id='log_"+result.method+"' class='FixedHeightContainer'></div>");
                            $('#log_'+result.method).prepend("<div id='"+result.method+"' class='Logs'>");
                        }
                        $("#"+result.method).prepend('<div>'+d.toLocaleString()+" - "+result.source+" = "+result.message+"</div>")
                        // message = light: 0.091553 lux
                        r = new RegExp(/\d*([.,\/]?\d+)/);
                        value = r.exec(result.message);
                        console.log(value[0]);
                        mydata.push([d,parseFloat(value[0])]);
                        drawVisualization();
                    }
                }
            }
        },

        send: function (msg)
        {
            if (socket) {
                socket.send(msg);
                console.log("Sent: " + msg);
            } else {
                console.log("Not connected.");
            }
        },

        resources: function()
        {

        }

    }
});
