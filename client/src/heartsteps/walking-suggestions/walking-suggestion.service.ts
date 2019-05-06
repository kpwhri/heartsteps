import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { WalkingSuggestionTimeService } from "./walking-suggestion-time.service";
import { ChoiceDialogController } from "@infrastructure/choice-dialog.controler";


@Injectable()
export class WalkingSuggestionService {

    constructor(
        private heartstepsServer: HeartstepsServer,
        private walkingSuggestionTimeService: WalkingSuggestionTimeService,
        private choiceDialog: ChoiceDialogController
    ){}

    sendDecisionContext(decisionId:string):Promise<boolean> {
        const decisionContext = {};
        return this.heartstepsServer.post('/walking-suggestions/'+decisionId, decisionContext)
        .then(() => {
            return true;
        });
    }

    createTestDecision(): Promise<boolean> {
        return this.walkingSuggestionTimeService.getTimeFields()
        .then((times:Array<any>) => {
            return this.choiceDialog.showChoices('Walking suggestion category', times.map((time:any) => {
                return {
                    text: time.name,
                    value: time.key
                }
            }))
            .then((value:any) => {
                return String(value);
            })
        })
        .then((category:string) => {
            return this.heartstepsServer.post('/walking-suggestions/', {
                category: category
            })
        })
        .then(() => {
            return true;
        });
    }
}
