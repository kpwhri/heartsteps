import { Component, OnInit } from "@angular/core";
import { Router } from "@angular/router";
import { LoadingService } from "@infrastructure/loading.service";
import { FormGroup, FormControl, Validators } from "@angular/forms";
import { AlertDialogController } from "@infrastructure/alert-dialog.controller";
import { FitbitClockFaceService } from '@heartsteps/fitbit-clock-face/fitbit-clock-face.service';


@Component({
    templateUrl: './fitbit-clock-face-pin.page.html'
})
export class FitbitClockFaceSettingsPage implements OnInit {

    public notificationsEnabled:boolean;
    public pin: string;
    public stepCounts: Array<any>;

    public form: FormGroup;

    constructor(
        private loadingService: LoadingService,
        private alertDialog: AlertDialogController,
        private fitbitClockFaceService: FitbitClockFaceService,
        private router: Router
    ) {}

    ngOnInit() {
        this.form = new FormGroup({
            'pin': new FormControl('', Validators.required)
        });
        this.updatePin()
        .then(() => {
            if(this.pin) {
                this.getLastStepCounts();
            }
        });
    }

    public goBack() {
        this.router.navigate([{
            outlets: {
                modal: null
            }
        }]);
    }

    public updatePin(): Promise<void> {
        this.loadingService.show('Updating pin');
        console.log('getting pin');
        return this.fitbitClockFaceService.getClockFace()
        .then((data) => {
            console.log('got pin');
            this.pin = data.pin;
        })
        .catch(() => {
            console.log('no pin');
            this.pin = undefined;
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    public getLastStepCounts(): Promise<void> {
        this.loadingService.show('Getting recent step count')
        return this.fitbitClockFaceService.getLastClockFaceLogs()
        .then((stepCounts) => {
            this.stepCounts = stepCounts;
        })
        .catch((error) => {
            this.alertDialog.show('Error: ' + error);
        })
        .then(() => {
            this.loadingService.dismiss()
        })
    }

    public deletePin(): Promise<void> {
        this.loadingService.show("Deleting pin");
        return this.fitbitClockFaceService.unpair()
        .then(() => {
            this.pin = undefined;
            this.stepCounts = undefined;
            this.alertDialog.show('Deleted');
        })
        .catch(() => {
            this.alertDialog.show('Error deleting pin');
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    public openFitbitGallery(): void {
        this.fitbitClockFaceService.openFitbitGallery();
    }

}
