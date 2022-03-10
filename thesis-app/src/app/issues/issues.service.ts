import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject } from 'rxjs/internal/BehaviorSubject';
import { map } from 'rxjs';
import { Issue } from './issue';

@Injectable({
  providedIn: 'root',
})
export class IssuesService {

  public issueHistorySubject = new BehaviorSubject<Issue[]>([]);

  public selectedProjectSubject = new BehaviorSubject<string>("");

  public generatedIssuesSubject = new BehaviorSubject<Issue[]>([]);

  constructor(private http: HttpClient) { }

  getIssues(params: any) {
    params.project = this.selectedProjectSubject.value.toLowerCase();
    return this.http.get<string[]>("http://localhost:5000/api/issues", {params: params}).pipe(
      map(x => x.map(y => 
        {    
          var issue = JSON.parse(y)
          issue.priority = issue["priority.name"]
          return issue;
        })));
  }

  getIssuesCount(params: any) {
    params.project = this.selectedProjectSubject.value.toLowerCase();
    return this.http.get<number>("http://localhost:5000/api/issuescount", {params: params});
  }

  getProjects() {
    return this.http.get<string[]>("http://localhost:5000/api/projects").pipe(
      map(x => x.map(y => JSON.parse(y))));
  }

  generateReccommendations(issues: Issue[]) {
    this.http.post<string[]>("http://localhost:5000/api/generate", issues.map(x => x.key)).pipe(
      map(x => x.map(y => 
        {    
          var issue = JSON.parse(y)
          issue.priority = issue["priority.name"]
          return issue;
        }))).subscribe((issues: Issue[]) => {
          this.generatedIssuesSubject.next(issues);
        });
  }

  addIssueToHistory(issue: Issue) {
    let history = this.issueHistorySubject.getValue();

    if (history.find(x => x.key == issue.key)) return;

    history.push(issue);

    this.issueHistorySubject.next(history);
  }

  remove(key: string) {
    let history = this.issueHistorySubject.getValue();

    let issue = history.find(x => x.key == key);

    if (!issue) return;

    let index = history.indexOf(issue);

    history.splice(index, 1);

    this.issueHistorySubject.next(history);
  }

  selectProject(key: string) {
    this.selectedProjectSubject.next(key);
    this.issueHistorySubject.next([])
    this.generatedIssuesSubject.next([])
  }

  submitFeedbackForm(data: any) {
    return this.http.post("http://localhost:5000/api/feedback", data)
  }
}
