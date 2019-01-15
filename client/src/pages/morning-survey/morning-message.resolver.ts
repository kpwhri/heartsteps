import { Injectable } from "@angular/core";
import { Resolve } from "@angular/router";
import { MorningMessage } from "@heartsteps/morning-message/morning-message.model";
import { MorningMessageService } from "@heartsteps/morning-message/morning-message.service";


@Injectable()
export class MorningMessageResolver implements Resolve<MorningMessage> {

    constructor(
        private morningMessageService: MorningMessageService
    ){}

    resolve() {
        return this.morningMessageService.get();
    }
}
