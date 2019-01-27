import { Component, Input, ComponentFactoryResolver, ViewChild, ViewContainerRef, EventEmitter, Output, OnInit, OnDestroy } from "@angular/core";
import { ActivatedRoute, Router, ParamMap } from "@angular/router";
import { Subscription } from "rxjs";

export class Step {
    key: string;
    title: string;
    component: any;
}

@Component({
    selector: 'heartsteps-stepper',
    templateUrl: './stepper.component.html',
    inputs: ['pages', 'param']
})
export class HeartstepsStepperComponent implements OnInit, OnDestroy {
    @ViewChild("container", { read: ViewContainerRef }) container: ViewContainerRef;

    private steps:Array<Step> = [];
    private param:string;
    private current_key:string;

    @Output('at-end') atEnd:EventEmitter<boolean> = new EventEmitter();
    @Output('at-start') atStart:EventEmitter<boolean> = new EventEmitter();

    private routeSubscription:Subscription;

    constructor(
        private activatedRoute: ActivatedRoute,
        private router: Router,
        private componentFactoryResolver: ComponentFactoryResolver
    ){}

    ngOnInit() {
        this.routeSubscription = this.activatedRoute.paramMap.subscribe((paramMap:ParamMap) => {
            this.getCurrentKey();
        });
    }

    ngOnDestroy() {
        this.routeSubscription.unsubscribe();
    }

    @Input('steps')
    set set_steps(steps:Array<Step>) {
        if(steps && steps.length > 0) {
            this.steps = steps;
            this.getCurrentKey();
        }
    }

    @Input('param')
    set set_param(param:string) {
        if(param) {
            this.param = param;
            this.getCurrentKey();
        }
    }

    private getCurrentKey() {
        if(this.param && this.steps && this.steps.length > 0) {
            const key:string = this.activatedRoute.snapshot.paramMap.get(this.param);
            if (key != this.current_key) {
                this.getStepIndex(key)
                .then((index) => {
                    this.goToStepNumber(index);
                })
                .catch(() => {
                    this.goToStepNumber(0);
                })
            }
        }
    }

    private loadStep(step:Step) {
        this.container.clear();

        const componentFactory = this.componentFactoryResolver.resolveComponentFactory(step.component);
        const componentRef = this.container.createComponent(componentFactory);

        this.current_key = step.key;

        const instance:any = componentRef.instance;
        const pageSubscription = instance.next.subscribe(() => {
            pageSubscription.unsubscribe();
            this.container.clear();
            this.nextStep();
        });
    }

    public nextStep(){
        this.getStepIndex(this.current_key)
        .then((index) => {
            this.goToStepNumber(index+1);
        });
    }

    public previousStep() {
        this.getStepIndex(this.current_key)
        .then((index) => {
            this.goToStepNumber(index-1);
        });
    }

    private goToStepNumber(index:number) {
        if (index >= this.steps.length) {
            this.atEnd.emit();
            return;
        }

        if (index <= 0) {
            this.atStart.emit();
            index = 0;
        }
        const step = this.steps[index];
        this.loadStep(step);
        this.router.navigate(['../' + step.key], {
            relativeTo: this.activatedRoute
        });
    }

    private getStepIndex(key) {
        const keys:Array<string> = this.steps.map((step) => {
            return step.key;
        });
        const index = keys.indexOf(key);
        if(index >= 0) {
            return Promise.resolve(index);
        } else {
            return Promise.reject("Step key not found");
        }
    }

}
