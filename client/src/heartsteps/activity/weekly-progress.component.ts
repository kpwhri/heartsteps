import { Component, ElementRef } from '@angular/core';
import * as d3 from 'd3';

const orderedAttributes: Array<string> = ['complete', 'today', 'incomplete'];

@Component({
    selector: 'heartsteps-weekly-progress',
    templateUrl: 'weekly-progress.html'
})
export class WeeklyProgressComponent {

    private pie:any;
    private arc: any;
    private pieGenerator: any;

    constructor(
        private elementRef:ElementRef
    ) {}

    ngOnInit() {
        const svg = d3.select(this.elementRef.nativeElement).append('svg');
        const width: number = this.elementRef.nativeElement.clientWidth;
        const height: number = this.elementRef.nativeElement.clientHeight;
        svg.attr('width', width);
        svg.attr('height', height);
        
        this.pie = svg.append('g');
        this.pie.attr('transform', 'translate(' + width/2 + ', ' + height/2 + ')');

        this.arc = d3.arc()
        .innerRadius(width/2 - 30)
        .outerRadius(width/2);

        this.pieGenerator = d3.pie()
        .value(function(d) {
            return d.value;
        })
        .sort(function(a, b) {
            let a_index = orderedAttributes.indexOf(a.name);
            let b_index = orderedAttributes.indexOf(b.name);

            if(a_index > b_index) {
                return 1;
            } else if (b_index > a_index) {
                return -1;
            } else {
                return 0;
            }
        });

        this.drawChart({
            'today': 0,
            'complete': 0,
            'incomplete': 150
        });
        setTimeout(() => {
            this.updateChart({
                'today': 10,
                'complete': 70,
                'incomplete': 70
            });
        }, 3000);
    }

    private drawChart(data:any) {
        const arcs = this.makeArcs(data);

        this.pie.selectAll("path")
        .data(arcs)
        .enter().append("path")
        .attr('class', d => {
            return d.data.name;
        })
        .attr('d', <any>this.arc)
        .each(function(d) {
            this._current = d;
        });


        this.pie.selectAll("path")
        .data(arcs)
        .attr('d', <any>this.arc);
    }

    private updateChart(data:any) {
        const arcs = this.makeArcs(data);
        const arcFunction = this.arc;

        this.pie.selectAll("path")
        .data(arcs)
        .transition().duration(1000)
        .attrTween("d", function(d) {
            const i = d3.interpolate(this._current, d);
            this._current = i(0);
            return function(t) {
                return arcFunction(i(t));
            }
        })
    }

    private makeArcs(data:any) {
        data = this.flattenData(data);
        return this.pieGenerator(data);
    }

    private flattenData(data:any):Array<any> {
        let dataArray:Array<any> = [];
        orderedAttributes.forEach((attr:string) => {
            dataArray.push({
                'value': data[attr],
                'name': attr
            });
        });
        return dataArray;
    }
}
