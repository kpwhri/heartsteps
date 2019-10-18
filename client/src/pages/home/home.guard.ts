import { Injectable } from "@angular/core";
import { CanActivate, Router } from "@angular/router";
import { AuthorizationService } from "@infrastructure/authorization.service";
import { ParticipantService } from "@heartsteps/participants/participant.service";

@Injectable()
export class HomeGuard implements CanActivate {

    constructor(
        private authorizationService: AuthorizationService,
        private participantService: ParticipantService,
        private router: Router
    ){}

    canActivate():Promise<boolean> {
        return this.authorizationService.isAuthorized()
        .then(() => {
            return true;
        })
        .catch(() => {
            return this.router.navigate(['/'])
            .then(() => {
                this.participantService.update();
                return false;
            });
        });
    }

}
