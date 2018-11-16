import { Component, ElementRef, OnInit, OnDestroy } from '@angular/core';
import * as d3 from 'd3';
import { DailySummary } from './daily-summary.model';
import { DateFactory } from '@infrastructure/date.factory';
import { DailySummaryService } from './daily-summary.service';
import { Subscription } from 'rxjs';

const COMPLETE:string = 'complete';
const TODAY: string = 'today';
const INCOMPLETE: string = 'incomplete';
const orderedAttributes: Array<string> = [COMPLETE, TODAY, INCOMPLETE];

@Component({
    selector: 'heartsteps-weekly-progress',
    templateUrl: 'weekly-progress.html',
    providers: [
        DateFactory
    ]
})
export class WeeklyProgressComponent implements OnInit, OnDestroy {

    private pie:any;
    private arc: any;
    private pieGenerator: any;

    private total: number;
    private complete: number;
    private current: number;

    private summarySubscription: Subscription;

    constructor(
        private elementRef:ElementRef,
        private dailySummaryService: DailySummaryService,
        private dateFactory: DateFactory
    ) {
        this.total = 150;
        this.complete = 0;
        this.current = 0;
    }

    ngOnInit() {
        this.initializeChart();
        this.drawChart();

        const currentWeek = this.dateFactory.getCurrentWeek();
        const start:Date = currentWeek[0];
        const end:Date = currentWeek.reverse()[0];

        this.summarySubscription = this.dailySummaryService.summaries.subscribe((summaries:Array<DailySummary>) => {
            this.complete = 0;
            this.current = 0;
            const today:string = this.dailySummaryService.formatDate(new Date());
            summaries.forEach((summary:DailySummary) => {
                this.complete += summary.totalMinutes;
                if(summary.date == today) {
                    this.current = summary.totalMinutes;
                }
            })
            this.updateChart();
        });
        this.dailySummaryService.getWeek(start, end);
    }

    ngOnDestroy() {
        this.summarySubscription.unsubscribe();
    }

    private initializeChart() {
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
        let completed = this.complete - this.current;
        if(completed > this.total - this.current) {
            completed = this.total - this.current;
        }
        let incomplete = this.total - this.complete;
        if(incomplete < 0) {
            incomplete = 0;
        }

        let data = [{
            'name': COMPLETE,
            'value': completed
        }, {
            'name': INCOMPLETE,
            'value': incomplete
        }, {
            'name': TODAY,
            'value': this.current
        }];
        return this.pieGenerator(data);
    }
}
