__author__ = 'Miklas Njor - iAmGoldenboy - http://miklasnjor.com'
__projectname__ = 'whos_news / lib_graphics.py'
__datum__ = '22/02/17'



def pieChart( uniqueDataName, dataDict, chartID, width=200, height=200, color="category20c()"):


    area = """  var w = {};
                var h = {};
                var r = h/2;
                var legendRectSize = 18;                                  // NEW
        var legendSpacing = 4;                                    // NEW

                """.format(width, height)

    colour = """ var color = d3.scale.{};

                """.format(color)

    dataListDict = """ var data_{} = {};

		          """.format(uniqueDataName, dataDict)


    selector = """ var vis = d3.select('{}').append("svg:svg").data([data_{}]).attr("width", {}).attr("height", {}).append("svg:g").attr("transform", "translate(" + r + "," + r + ")");

                    """.format(chartID, uniqueDataName, width, height)

    churn = """ var pie = d3.layout.pie().value(function(d){return d.value;});

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

        var legend = svg.selectAll('.legend')                     // NEW
          .data(color.domain())                                   // NEW
          .enter()                                                // NEW
          .append('g')                                            // NEW
          .attr('class', 'legend')                                // NEW
          .attr('transform', function(d, i) {                     // NEW
            var height = legendRectSize + legendSpacing;          // NEW
            var offset =  height * color.domain().length / 2;     // NEW
            var horz = -2 * legendRectSize;                       // NEW
            var vert = i * height - offset;                       // NEW
            return 'translate(' + horz + ',' + vert + ')';        // NEW
          });                                                     // NEW

        legend.append('rect')                                     // NEW
          .attr('width', legendRectSize)                          // NEW
          .attr('height', legendRectSize)                         // NEW
          .style('fill', color)                                   // NEW
          .style('stroke', color);                                // NEW

        legend.append('text')                                     // NEW
          .attr('x', legendRectSize + legendSpacing)              // NEW
          .attr('y', legendRectSize - legendSpacing)              // NEW
          .text(function(d) { return d; });                       // NEW

                // add the text
                arcs.append("svg:text").attr("transform", function(d){
                            d.innerRadius = 0;
                            d.outerRadius = r;
                    return "translate(" + arc.centroid(d) + ")";}).attr("text-anchor", "middle").text( function(d, i) {"""

    churn += """                return data_{}[i].label;""".format(uniqueDataName)

    churn += """}
                        );
                """

    return "{} {} {} {} {}".format(area, colour, dataListDict, selector, churn)



def pieChart2( uniqueDataName, dataDict, chartID, width=200, height=200, donutwidth=75, legendRectSize=18, legendSpacing=4, color="schemeCategory20b"):

    bakedPie = """(function(d3) {
                """

    bakedPie +=   """
        'use strict';

        var dataset = {};

        var width = {};
        var height = {};
        var radius = Math.min(width, height) / 2;
        var donutWidth = {};
        var legendRectSize = {};
        var legendSpacing = {};

        var color = d3.scaleOrdinal(d3.{});

        var svg = d3.select('{}')
          .append('svg')
          .attr('width', width)
          .attr('height', height)
          .append('g')
          .attr('transform', 'translate(' + (width / 2) +
            ',' + (height / 2) + ')');

        var arc = d3.arc()
          .innerRadius(radius - donutWidth)
          .outerRadius(radius);
          """.format(dataDict, width, height, donutwidth, legendRectSize, legendSpacing, color, chartID)

    bakedPie +=    """
    var pie = d3.pie()
          .value(function(d) { return d.count; })
          .sort(null);
          """

    bakedPie +=    """
    var tooltip = d3.select('{}')
          .append('div')
          .attr('class', 'tooltip');

        tooltip.append('div')
          .attr('class', 'label');

        tooltip.append('div')
          .attr('class', 'count');

        tooltip.append('div')
          .attr('class', 'percent');
          """.format(chartID)

    bakedPie +=    """
    var path = svg.selectAll('path')
            .data(pie(dataset))
            .enter()
            .append('path')
            .attr('d', arc)
            .attr('fill', function(d, i) {
              return color(d.data.label);
            })                                                        // UPDATED (removed semicolon)
            .each(function(d) { this._current = d; });                // NEW

          path.on('mouseover', function(d) {
            var total = d3.sum(dataset.map(function(d) {
              return (d.enabled) ? d.count : 0;                       // UPDATED
            }));
            var percent = Math.round(1000 * d.data.count / total) / 10;
            tooltip.select('.label').html(d.data.label);
            tooltip.select('.count').html(d.data.count);
            tooltip.select('.percent').html(percent + '%');
            tooltip.style('display', 'block');
          });

          path.on('mouseout', function() {
            tooltip.style('display', 'none');
          });

          /* OPTIONAL
          path.on('mousemove', function(d) {
            tooltip.style('top', (d3.event.layerY + 10) + 'px')
              .style('left', (d3.event.layerX + 10) + 'px');
          });
          */

          var legend = svg.selectAll('.legend')
            .data(color.domain())
            .enter()
            .append('g')
            .attr('class', 'legend')
            .attr('transform', function(d, i) {
              var height = legendRectSize + legendSpacing;
              var offset =  height * color.domain().length / 2;
              var horz = -2 * legendRectSize;
              var vert = i * height - offset;
              return 'translate(' + horz + ',' + vert + ')';
            });

          legend.append('rect')
            .attr('width', legendRectSize)
            .attr('height', legendRectSize)
            .style('fill', color)
            .style('stroke', color)                                   // UPDATED (removed semicolon)
            .on('click', function(label) {                            // NEW
              var rect = d3.select(this);                             // NEW
              var enabled = true;                                     // NEW
              var totalEnabled = d3.sum(dataset.map(function(d) {     // NEW
                return (d.enabled) ? 1 : 0;                           // NEW
              }));                                                    // NEW

              if (rect.attr('class') === 'disabled') {                // NEW
                rect.attr('class', '');                               // NEW
              } else {                                                // NEW
                if (totalEnabled < 2) return;                         // NEW
                rect.attr('class', 'disabled');                       // NEW
                enabled = false;                                      // NEW
              }                                                       // NEW

              pie.value(function(d) {                                 // NEW
                if (d.label === label) d.enabled = enabled;           // NEW
                return (d.enabled) ? d.count : 0;                     // NEW
              });                                                     // NEW

              path = path.data(pie(dataset));                         // NEW

              path.transition()                                       // NEW
                .duration(750)                                        // NEW
                .attrTween('d', function(d) {                         // NEW
                  var interpolate = d3.interpolate(this._current, d); // NEW
                  this._current = interpolate(0);                     // NEW
                  return function(t) {                                // NEW
                    return arc(interpolate(t));                       // NEW
                  };                                                  // NEW
                });                                                   // NEW
            });                                                       // NEW

          legend.append('text')
            .attr('x', legendRectSize + legendSpacing)
            .attr('y', legendRectSize - legendSpacing)
            .text(function(d) { return d; });

        });

      })(window.d3);
      """


    return bakedPie

def testpie(pieData):

    pieChars =  """
                (function(d3) {
        'use strict';
        """

    pieChars += """    var dataset = {} ;""".format(pieData)

    pieChars += """    var width = 460;
        var height = 360;
        var radius = Math.min(width, height) / 2;
        var donutWidth = 180;
        var legendRectSize = 18;                                  // NEW
        var legendSpacing = 4;                                    // NEW

        var color = d3.scaleOrdinal(d3.schemeCategory20b);



        var svg = d3.select('#chart')
          .append('svg')
          .attr('width', width)
          .attr('height', height)
          .append('g')
          .attr('transform', 'translate(' + (width / 2) +
            ',' + (height / 2) + ')');

        var arc = d3.arc()
          .innerRadius(radius - donutWidth)
          .outerRadius(radius - (donutWidth-70));

        var pie = d3.pie()
          .value(function(d) { return d.count; })
          .sort(null);

        var tooltip = d3.select('#chart')                               // NEW
          .append('div')                                                // NEW
          .attr('class', 'tooltipe');                                    // NEW

        tooltip.append('div')                                           // NEW
          .attr('class', 'label');                                      // NEW

        tooltip.append('div')                                           // NEW
          .attr('class', 'count');                                      // NEW

        tooltip.append('div')                                           // NEW
          .attr('class', 'percent');                                    // NEW

        var path = svg.selectAll('path')
          .data(pie(dataset))
          .enter()
          .append('path')
          .attr('d', arc)
          .attr('fill', function(d, i) {
            return color(d.data.label);
          });

        path.on('mouseover', function(d) {                            // NEW
            var total = d3.sum(dataset.map(function(d) {                // NEW
              return d.count;                                           // NEW
            }));                                                        // NEW
            var percent = Math.round(1000 * d.data.count / total) / 10; // NEW
            tooltip.select('.label').html(d.data.label);                // NEW
            tooltip.select('.count').html(d.data.count);                // NEW
            tooltip.select('.percent').html(percent + '%');             // NEW
            tooltip.style('display', 'block');                          // NEW
          });                                                           // NEW

          path.on('mouseout', function() {                              // NEW
            tooltip.style('display', 'none');                           // NEW
          });

        var legend = svg.selectAll('.legend')                     // NEW
          .data(color.domain())                                   // NEW
          .enter()                                                // NEW
          .append('g')                                            // NEW
          .attr('class', 'legend')                                // NEW
          .attr('transform', function(d, i) {                     // NEW
            var height = legendRectSize + legendSpacing;          // NEW
            var offset =  height * color.domain().length / 2;     // NEW
            var horz = 5 * legendRectSize;                       // NEW
            var vert = i * height - offset;                       // NEW
            return 'translate(' + horz + ',' + vert + ')';        // NEW
          });                                                     // NEW

        legend.append('rect')                                     // NEW
          .attr('width', legendRectSize)                          // NEW
          .attr('height', legendRectSize)                         // NEW
          .style('fill', color)                                   // NEW
          .style('stroke', color);                                // NEW

        legend.append('text')                                     // NEW
          .attr('x', legendRectSize + legendSpacing)              // NEW
          .attr('y', legendRectSize - legendSpacing)              // NEW
          .text(function(d) { return d; });                       // NEW

      })(window.d3);
     """

    return pieChars