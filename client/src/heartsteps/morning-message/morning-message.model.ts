
export class MorningMessage {
    id:string;
    date:Date;
    notification: string;
    text:string;
    anchor:string;
    survey: any;
    response: any;

    public isComplete():boolean {
        if(this.survey && this.survey.completed) {
            return true;
        } else {
            return false;
        }
    }
}
