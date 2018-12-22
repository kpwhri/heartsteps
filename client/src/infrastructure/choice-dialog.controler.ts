import { Injectable } from "@angular/core";
import { ActionSheetController } from "ionic-angular";

@Injectable()
export class ChoiceDialogController {

    constructor(
        private actionSheetCtrl: ActionSheetController
    ) {}

    public showChoices(title:string, choices:Array<any>):Promise<any> {
        return new Promise((resolve, reject) => {
            const buttonChoices = [];

            choices.forEach((choice:any) => {
                buttonChoices.push({
                    text: choice.text,
                    handler: () => {
                        resolve(choice.value);
                    }
                })
            });

            buttonChoices.push({
                text: 'Cancel',
                handler: () => {
                    reject();
                }
            });
        
            const actionSheet = this.actionSheetCtrl.create({
                title: title,
                buttons: buttonChoices
            });
            actionSheet.present();
        })
    }
}