import { Injectable } from "@angular/core";
import { LoadingController, Loading } from "ionic-angular";

@Injectable()
export class LoadingService {

    private loader:Loading
    private showingLoader:Boolean

    constructor(
        private loadingCtrl:LoadingController
    ) {}

    show(message:string) {
        if(!this.showingLoader) {
            this.loader = this.loadingCtrl.create({
                spinner: 'crescent',
            })

            this.loader.onWillDismiss(() => {
                this.showingLoader = false;
            })

            this.showingLoader = true
        }
        this.loader.setContent(message)
        this.loader.present()
    }

    dismiss() {
        setTimeout(() => {
            this.loader.dismiss()
        }, 500)
    }

}