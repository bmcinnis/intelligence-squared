window.onload=function (){
    var loadedLibs = [];
    if (typeof jQuery=='undefined') {
        loadedLibs.push("jquery"); 
    }
    if (typeof d3=='undefined') {
        loadedLibs.push("d3"); 
    }
    if (loadedLibs.length>0) {
        alert("Not Loaded: "+loadedLibs.join(","));            
    }else{
        init();
    }
};        
var init = function(){
    /*  On reload ping the server for the latest list of i2us debates  */    
    
    $("div#full-text").hide();
    $("div#debate-description").hide();
    $("svg#debateChart").hide();    
    
    function circleHover(item, selector,obj) {        
        var oKeys = Object.keys(obj);
        for (var a = 0; a<oKeys.length;a++) {
            $(selector).find(oKeys[a]).html(obj[oKeys[a]]);
        }
    }                
                
    $.post("http://"+location.host, JSON.stringify({'action':'reload-debates'}))
        .done(function(ret) {
            ret = JSON.parse(ret);
            for (var r = 0; r<ret['debate-list'].length; r++) {
                $("select#select-debate").append("<option id='"+r+"'>"+ret['debate-list'][r]+"</option>");
            }
        });

    var svg = d3.select("svg#debateChart");
    
    var w = svg.style("width"),
        h = svg.style("height");

    var x = d3.scale.linear()
                .domain([0, 1])
                .range([0, w]);

    var y = d3.scale.linear()
                .domain([0, 1])
                .range([0, h]);


    function updateChart(data,yaxis){
        
        var randAxis = [];
        for(var q=0;q<data.length;q++){
            randAxis.push(Math.random());            
        }
        
        var line = d3.svg.line()
            .x(function(d,i) { return String(x(((i+0.5)/data.length))).match(/([0-9.]+)px$/)[1]; })
            .y(function(d,i) { return String(y(randAxis[i])).match(/([0-9.]+)px$/)[1]; });
                    
        svg.append("path")
            .attr("class", "line")
            .attr("d", line(data));                    
                    
        svg.selectAll("circle")
            .data(data)
          .enter().append("circle")
            .attr("id", function(d,i){ return i;})
            .attr("r", 5)
            .attr("cy", function(d,i){ return y(randAxis[i]); })
            .attr("cx", function(d,i){ return x(((i+0.5)/data.length)); })
            .on('mouseover',function(d,i){
                                    var tQuote = "";
                                    for (var a=0; a<d["FULL-TEXT"].length;a++){
                                        tQuote += "<p>"+d["FULL-TEXT"][a]+"</p>";
                                    }
                                    circleHover(
                                            item=i,
                                            selector="div#full-text",
                                            obj={'h3': d["SPEAKER"],
                                                'blockquote': tQuote,
                                                'em': 'Statement '+i});
                                            }                                        
                                    );
        
    };
                        
    $(document).on('change','select#select-debate',function(){
            if ($(this).val()!="") {
                $("div#full-text").hide('fast');
                $("div#debate-description").hide('fast');
                $("svg#debateChart").hide('fast');

                svg.selectAll("circle")
                    .remove();
                svg.selectAll("path")
                    .remove();

                $.post("http://"+location.host, JSON.stringify({'action':'retrieve-debates',
                                                               'data':$(this).val()}))
                    .done(function(ret) {
                                                            
                        // Create some function to process the ret data, get max/min

                        ret = JSON.parse(ret);
                        //alert(Object.keys(ret));
                                                        
                        updateChart(data=ret['debate-content']['text']);
                        
                        var quote = ret['debate-content']['text'][0]["FULL-TEXT"];
                        var tQuote = "";
                        for (var a=0; a<quote.length;a++){
                            tQuote += "<p>"+quote[a]+"</p>";
                        }
                        circleHover(item=0,
                                    selector="div#full-text",
                                    obj={'h3': ret['debate-content']['text'][0]["SPEAKER"],
                                        'blockquote': tQuote,
                                        'em': 'Statement '+0});
                    });
                $("div#full-text").show('fast');
                $("div#debate-description").show('fast');
                $("svg#debateChart").show('fast');
            }
        });
        
    $(document).on('click','span[class^="link-"]',function(){
            var classes = $(this).attr('class');
            classes = classes.split(" ");
            for (var i =0;i<classes.length; i++){
                if (classes[i].match(/^link-(.*)$/)) {
                    switch(classes[i].match(/^link-(.*)$/)[1]){
                        case 'github':
                            window.open('https://github.com/bmcinnis/intelligence-squared');
                            break;
                        case 'post':
                            var dataPost = [];
                            if ($(this).data('post') != null) {
                                dataPost.append({'dataPost':$(this).data('post')});                                
                            }                            
                            alert("POST http://"+location.host);                           
                            $.post("http://"+location.host, JSON.stringify(dataPost))
                                .done(function(ret) {
                                    alert(ret);
                                });
                            break;
                        case 'cuis':
                            window.open('http://infosci.cornell.edu/');
                            break;
                        case 'cuis-bjm':
                            window.open('http://infosci.cornell.edu/forward-thinking-people/phds/brian-mcinnis');
                            break;
                    }                            
                }
            }            
        });
};