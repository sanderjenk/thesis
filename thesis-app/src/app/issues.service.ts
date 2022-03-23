import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject } from 'rxjs/internal/BehaviorSubject';
import { map } from 'rxjs';
import { Issue } from './issue';

@Injectable({
  providedIn: 'root',
})
export class IssuesService {

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

  getDevelopers() {
    let project = this.selectedProjectSubject.value.toLowerCase();
    return this.http.get<string[]>("http://localhost:5000/api/developers" , {params: {project}}).pipe(
      map(x => x.map(y => JSON.parse(y))));
    }

  generateReccommendations(storypoints: number, developer: string) {
    let project = this.selectedProjectSubject.value.toLowerCase();
    return this.http.post<string[]>("http://localhost:5000/api/generate", {}, {params: {project, storypoints, username: developer}});
  }

  getVelocity(developer: string) {
    let project = this.selectedProjectSubject.value.toLowerCase();
    return this.http.get<number>("http://localhost:5000/api/velocity", {params: {username: developer, project}})
  } 

  selectProject(key: string) {
    this.selectedProjectSubject.next(key);
    this.generatedIssuesSubject.next([])
  }

  submitFeedbackForm(data: any) {
    return this.http.post("http://localhost:5000/api/feedback", data)
  }
}
