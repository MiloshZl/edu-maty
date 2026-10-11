export function average(grades) {
  const valid = grades.filter(g=>g.kind==='numeric' && g.included===true && Number.isFinite(g.value) && g.value>=1 && g.value<=5 && Number.isFinite(g.weight) && g.weight>0);
  return {value:valid.length ? valid.reduce((s,g)=>s+g.value*g.weight,0)/valid.reduce((s,g)=>s+g.weight,0) : null, excluded:grades.length-valid.length};
}
export function localDate(date = new Date()) {
  return new Intl.DateTimeFormat('en-CA',{timeZone:'Europe/Prague',year:'numeric',month:'2-digit',day:'2-digit'}).format(date);
}
export function weekStart(date=localDate()) {
  const d=new Date(date+'T12:00:00Z'); d.setUTCDate(d.getUTCDate()-((d.getUTCDay()+6)%7)); return d.toISOString().slice(0,10);
}
export function addDays(date, days) {
  const d=new Date(date+'T12:00:00Z'); d.setUTCDate(d.getUTCDate()+days); return d.toISOString().slice(0,10);
}
