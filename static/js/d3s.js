
var w = 400;
var h = 400;
var r = h/2;
var color = d3.scale.category20c();

var data = [{"label":"Category A", "value":20},
		          {"label":"Category B", "value":50},
		          {"label":"Category C", "value":30}];


var vis = d3.select('#chart').append("svg:svg").data([data]).attr("width", w).attr("height", h).append("svg:g").attr("transform", "translate(" + r + "," + r + ")");
var pie = d3.layout.pie().value(function(d){return d.value;});

// declare an arc generator function
var arc = d3.svg.arc().outerRadius(r);

// select paths, use arc generator to draw
var arcs = vis.selectAll("g.slice").data(pie).enter().append("svg:g").attr("class", "slice");
arcs.append("svg:path")
    .attr("fill", function(d, i){
        return color(i);
    })
    .attr("d", function (d) {
        // log the result of the arc generator to show how cool it is :)
        console.log(arc(d));
        return arc(d);
    });

// add the text
arcs.append("svg:text").attr("transform", function(d){
			d.innerRadius = 0;
			d.outerRadius = r;
    return "translate(" + arc.centroid(d) + ")";}).attr("text-anchor", "middle").text( function(d, i) {
    return data[i].label;}
		);


  var w = 200;
                var h = 200;
                var r = h/2;

                  var color = d3.scale.category20c();

                  var firstpie = [[{&#39;value&#39;: 62.39, &#39;label&#39;: &#39;Udland 62.39% (136)&#39;}, {&#39;value&#39;: 35.32, &#39;label&#39;: &#39;Indland 35.32% (77)&#39;}, {&#39;value&#39;: 0.92, &#39;label&#39;: &#39;Politik 0.92% (2)&#39;}, {&#39;value&#39;: 0.92, &#39;label&#39;: &#39;Kultur 0.92% (2)&#39;}, {&#39;value&#39;: 0.46, &#39;label&#39;: &#39;Økonomi 0.46% (1)&#39;}]];

		            var vis = d3.select(&#39;#firstpie&#39;).append(&#34;svg:svg&#34;).data([firstpie]).attr(&#34;width&#34;, 200).attr(&#34;height&#34;, 200).append(&#34;svg:g&#34;).attr(&#34;transform&#34;, &#34;translate(&#34; + r + &#34;,&#34; + r + &#34;)&#34;);

                      var pie = d3.layout.pie().value(function(d){return d.value;});

                // declare an arc generator function
                var arc = d3.svg.arc().outerRadius(r);

                // select paths, use arc generator to draw
                var arcs = vis.selectAll(&#34;g.slice&#34;).data(pie).enter().append(&#34;svg:g&#34;).attr(&#34;class&#34;, &#34;slice&#34;);
                arcs.append(&#34;svg:path&#34;)
                    .attr(&#34;fill&#34;, function(d, i){
                        return color(i);
                    })
                    .attr(&#34;d&#34;, function (d) {
                        // log the result of the arc generator to show how cool it is :)
                        console.log(arc(d));
                        return arc(d);
                    });

                // add the text
                arcs.append(&#34;svg:text&#34;).attr(&#34;transform&#34;, function(d){
                            d.innerRadius = 0;
                            d.outerRadius = r;
                    return &#34;translate(&#34; + arc.centroid(d) + &#34;)&#34;;}).attr(&#34;text-anchor&#34;, &#34;middle&#34;).text( function(d, i) {
                    return data[i].label;}
                        );
