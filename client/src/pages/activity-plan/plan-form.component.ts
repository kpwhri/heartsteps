import { Component, Input, OnInit, Output, EventEmitter, ViewChild } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';

import { ActivityPlanService } from '@heartsteps/activity-plans/activity-plan.service';
import { ActivityPlan } from '@heartsteps/activity-plans/activity-plan.model';
import { DateFactory } from '@infrastructure/date.factory';
import { FormComponent } from '@infrastructure/form/form.component';
import { LoadingService } from '@infrastructure/loading.service';
import { ModalDialogController } from '@infrastructure/dialogs/modal-dialog.controller';
import { ActivityEnjoyedModalComponent } from '@heartsteps/activity-logs/activity-enjoyed-modal.component';

@Component({
    selector: 'activity-plan-form',
    templateUrl: './plan-form.component.html',
    providers: [
        DateFactory,
        ModalDialogController
    ]
})
export class PlanFormComponent implements OnInit {

    @Output() saved = new EventEmitter<boolean>();
    @ViewChild(FormComponent) form: FormComponent;

    public activityPlan:ActivityPlan;
    public availableDates:Array<Date>;

    public planForm:FormGroup;
    public error:string;

    public updateView:boolean;

    constructor(
        private activityPlanService:ActivityPlanService,
        private dateFactory: DateFactory,
        private loadingService: LoadingService,
        private modalDialog: ModalDialogController
    ) {}

    ngOnInit() {
        this.availableDates = this.dateFactory.getCurrentWeek();
    }

    @Input('plan')
    set plan(activityPlan:ActivityPlan) {
        if(activityPlan) {
            this.activityPlan = activityPlan;
            this.planForm = new FormGroup({
                activity: new FormControl(this.activityPlan.type, Validators.required),
                duration: new FormControl(this.activityPlan.duration || 30, Validators.required),
                date: new FormControl(this.activityPlan.start, Validators.required),
                time: new FormControl(this.activityPlan.start, Validators.required),
                vigorous: new FormControl(this.activityPlan.vigorous, Validators.required)
            });
            
            if(activityPlan.complete) {
                this.planForm.disable();
            }

            if(activityPlan.id) {
                this.updateView = true;
            } else {
                this.updateView = false;
            }
        }
    }

    updateActivity() {
        this.activityPlan.type = this.planForm.value.activity;
        this.activityPlan.duration = this.planForm.value.duration;
        this.activityPlan.vigorous = this.planForm.value.vigorous;
        this.activityPlan.start.setFullYear(this.planForm.value.date.getFullYear());
        this.activityPlan.start.setMonth(this.planForm.value.date.getMonth());
        this.activityPlan.start.setDate(this.planForm.value.date.getDate());
        this.activityPlan.start.setHours(this.planForm.value.time.getHours());
        this.activityPlan.start.setMinutes(this.planForm.value.time.getMinutes());
    }

    private validateActivity():Promise<ActivityPlan> {
        return this.form.submit()
        .then(() => {
            this.updateActivity();
            return this.activityPlan;
        });
    }

    public save() {
        this.loadingService.show('Saving activity plan');
        return this.validateActivity()
        .then((activityPlan) => {
            return this.activityPlanService.save(activityPlan);
        })
        .then(() => {
            this.saved.emit();
        })
        .catch((error) => {
            this.error = error;
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    public complete() {
        this.loadingService.show('Completing activity plan');
        this.validateActivity()
        .then((activityPlan) => {
            return this.activityPlanService.complete(activityPlan);
        })
        .then((plan) => {
            this.loadingService.dismiss();
            return this.rateActivity(plan)
        })
        .then(() => {
            this.saved.emit();
        })
        .catch((error) => {
            this.error = error;
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    private rateActivity(plan: ActivityPlan): Promise<boolean> {
        return this.modalDialog.createModal(ActivityEnjoyedModalComponent, {
            activityLogId: plan.activityLogId
        })
        .then(() => {
            return Promise.resolve(true);
        });
    }

    public uncomplete() {
        this.loadingService.show('Uncompleting activity plan');
        this.activityPlanService.uncomplete(this.activityPlan)
        .then(() => {
            this.saved.emit();
        })
        .catch((error) => {
            this.error = error;
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    public delete() {
        this.activityPlanService.delete(this.activityPlan)
        .then(() => {
            this.saved.emit();
        })
        .catch((error) => {
            this.error = error;
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

}