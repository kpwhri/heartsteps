import { Component, OnInit } from "@angular/core";
import { Router } from "@angular/router";
import { LoadingService } from "@infrastructure/loading.service";
import { FormGroup, FormControl, Validators } from "@angular/forms";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { AlertDialogController } from "@infrastructure/alert-dialog.controller";



@Component({
    templateUrl: './fitbit-clock-face-pin.page.html'
})
export class FitbitClockFacePinPage implements OnInit {

    public notificationsEnabled:boolean;
    public pin: string;

    public form: FormGroup;

    constructor(
        private heartstepsServer:HeartstepsServer,
        private loadingService: LoadingService,
        private alertDialog: AlertDialogController,
        private router: Router
    ) {}

    ngOnInit() {
        this.form = new FormGroup({
            'pin': new FormControl('', Validators.required)
        });
        this.updatePin();
    }

    public goBack() {
        this.router.navigate([{
            outlets: {
                modal: null
            }
        }]);
    }

    public submitForm() {
        if(this.form.valid) {
            this.loadingService.show('Pairing Fitbit Clock Face')
            this.heartstepsServer.post('pin_gen/pair/', {
                'pin': this.form.get('pin').value
            })
            .then(() => {
                this.alertDialog.show('Successfully paired!')
                .then(() => {
                    this.updatePin()
                });
            })
            .catch(() => {
                this.alertDialog.show('Error pairing');
            })
            .then(() => {
                this.loadingService.dismiss()
            });
        }
    }

    public updatePin(): Promise<void> {
        this.loadingService.show('Updating pin');
        return this.heartstepsServer.get('pin_gen/pair/')
        .then((data) => {
            this.pin = data.pin;
        })
        .catch(() => {
            this.pin = undefined;
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

}
