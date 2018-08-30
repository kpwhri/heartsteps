import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';
import { ContactInformationService } from '@heartsteps/contact-information.service';
import { loadingService } from '@infrastructure/loading.service';
import { FormBuilder, Validators } from '@angular/forms';

@Component({
    selector: 'participant-information-page',
    templateUrl: 'participant-information.html'
})
export class ParticipantInformationPage {

    public contactInformationForm: any

    constructor(
        private navCtrl:NavController,
        private contactInformationService:ContactInformationService,
        private loadingService:loadingService,
        private formBuilder:FormBuilder
    ) {
        this.contactInformationService.get()
        .then((contactInformation:any) => {
            return contactInformation
        })
        .catch(() => {
            return {
                name: '',
                email: '',
                phone: ''
            }
        })
        .then((contactInformation) => {
            this.contactInformationForm = this.formBuilder.group({
                name: [contactInformation.name, Validators.required],
                email: [contactInformation.email, [Validators.email, Validators.required]],
                phone: [contactInformation.phone, Validators.required]
            })
        })
    }

    save() {
        if(this.contactInformationForm.valid) {
            this.loadingService.show('Saving contact information')
            this.contactInformationService.save(this.contactInformationForm.value)
            .then(() => {
                this.navCtrl.pop()
            })
            .then(() => {
                this.loadingService.dismiss()
            })
        }
    }

}
