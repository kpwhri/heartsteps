import { Component, OnInit } from "@angular/core";
import { ActivatedRoute, Router } from "@angular/router";
import { ActivityPlan } from "@heartsteps/activity-plans/activity-plan.model";
import { Location } from "@angular/common";
import { ActivityPlanService } from "@heartsteps/activity-plans/activity-plan.service";
import { LoadingService } from "@infrastructure/loading.service";
import { AlertDialogController } from "@infrastructure/alert-dialog.controller";

@Component({
    templateUrl: './activity-plan.page.html'
})
export class ActivityPlanPage implements OnInit {

    public activityPlan: ActivityPlan;

    constructor(
        private activityPlanService: ActivityPlanService,
        private loadingService: LoadingService,
        private alertDialogController: AlertDialogController,
        private activatedRoute: ActivatedRoute,
        private location: Location,
        private router: Router
    ){}

    public ngOnInit() {
        this.activityPlan = this.activatedRoute.snapshot.data['activityPlan'];
    }

    public complete() {
        this.router.navigate(['plans', this.activityPlan.id, 'complete']);
    }

    public delete() {
        this.loadingService.show('Deleting activity plan');
        this.activityPlanService.delete(this.activityPlan)
        .then(() => {
            this.dismiss();
        })
        .catch((error) => {
            this.alertDialogController.show(error);
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    public dismiss() {
        this.location.back();
    }

}
