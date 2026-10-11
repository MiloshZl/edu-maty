import {test} from 'node:test';
import assert from 'node:assert/strict';
import {average, localDate, weekStart, addDays} from '../src/calculations.js';
const g=(value,weight,included=true,kind='numeric')=>({value,weight,included,kind});
test('weighted average, future simulation and removing hypothetical grades',()=>{
  const original=[g(1,1),g(3,2)];assert.equal(average(original).value,7/3);
  assert.equal(average([...original,g(1,3)]).value,10/6);assert.equal(average(original).value,7/3);
});
test('unknown weights, inclusion, points and plus-minus stay excluded',()=>{
  assert.deepEqual(average([g(1,1),g(2,null),g('1-',1),g(90,1,true,'percent'),g(2,0),g(2,Infinity),g(2,1,null)]),{value:1,excluded:6});
  assert.equal(average([]).value,null);
});
test('Prague date across midnight and DST and school week',()=>{
  assert.equal(localDate(new Date('2026-10-06T22:01:00Z')),'2026-10-07');
  assert.equal(localDate(new Date('2026-10-25T01:30:00Z')),'2026-10-25');
  assert.equal(weekStart('2026-10-11'),'2026-10-05');
  assert.equal(addDays('2026-10-24',2),'2026-10-26');
});
