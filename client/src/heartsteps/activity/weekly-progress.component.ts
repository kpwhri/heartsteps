import { Component, ElementRef } from '@angular/core';
import * as d3 from 'd3';
import { WeeklyProgressService, WeeklyProgressSummary } from './weekly-progress.service';
import { DailySummaryFactory } from './daily-summary.factory';
import { DailySummary } from './daily-summary.model';
import { DateFactory } from '@infrastructure/date.factory';

const COMPLETE:string = 'complete';
const TODAY: string = 'today';
const INCOMPLETE: string = 'incomplete';
const orderedAttributes: Array<string> = [COMPLETE, TODAY, INCOMPLETE];

@Component({
    selector: 'heartsteps-weekly-progress',
    templateUrl: 'weekly-progress.html',
    providers: [
        DailySummaryFactory,
        WeeklyProgressService,
        DateFactory
    ]
})
export class WeeklyProgressComponent {

    private pie:any;
    private arc: any;
    private pieGenerator: any;

    private total: number;
    private complete: number;
    private current: number;

    constructor(
        private elementRef:ElementRef,
        private weeklyProgressService:WeeklyProgressService,
        private dailySummary:DailySummaryFactory,
        dateFactory: DateFactory
    ) {
        this.total = 0;
        this.complete = 0;
        this.current = 0;

        const currentWeek = dateFactory.getCurrentWeek();
        const start:Date = currentWeek[0];
        const end:Date = currentWeek.reverse()[0];
        this.weeklyProgressService.getSummary(start, end).subscribe((summary:WeeklyProgressSummary) => {
            this.total = summary.goal;
            this.complete = summary.completed;
            this.updateChart();
        });
    }

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
        .value(<any>function(d) {
            return d.value;
        })
        .sort(<any>function(a, b) {
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

        this.drawChart();
    }

    private drawChart() {
        const arcs = this.makeArcs();

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

    private updateChart() {
        const arcs = this.makeArcs();
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

    private makeArcs() {
        let data = [{
            'name': COMPLETE,
            'value': this.complete - this.current
        }, {
            'name': INCOMPLETE,
            'value': this.total - this.complete
        }, {
            'name': TODAY,
            'value': this.current
        }];
        return this.pieGenerator(data);
    }
}
