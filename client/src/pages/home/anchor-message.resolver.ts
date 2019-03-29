import { Injectable } from "@angular/core";
import { Resolve } from "@angular/router";
import { AnchorMessageService } from "@heartsteps/anchor-message/anchor-message.service";


@Injectable()
export class AnchorMessageResolver implements Resolve<string> {

    constructor(
        private anchorMessageService: AnchorMessageService
    ){}

    resolve() {
        return this.anchorMessageService.get()
    }
}
