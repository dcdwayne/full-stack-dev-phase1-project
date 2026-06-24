// 程式好不好？？非單一面向的問題喔
// 案例示範，輸入一筆整數陣列，例如[ 3, -5, -2, 8, -10]，找到兩兩相乘結果最大值 印出來

// O(N^2)
function test1(data){
    let max = data[0]*data[1];
    for (let i=0; i<data.length; i++){
        for (let j=0; j<data.length; j++){
            if(i ===j){
                continue;
            }
            if(data[i]*data[j]>max){
                max = data[i]*data[j];
            }
        }
    }
    console.log(max);
}

// O(N*log(N))
function test2(data){
    let sortedData = data.toSorted((a, b)=>(a-b));
    // 比比看最小的兩個相乘，和最大的兩個相乘，誰比較大，誰就是答案
    // console.log(sortedData);
    let max = sortedData[0]*sortedData[1];
    if (sortedData[sortedData.length-1]*sortedData[sortedData.length-2]>max){
        max = sortedData[sortedData.length-1]*sortedData[sortedData.length-2];
    }
    console.log(max);
}

// 線性時間複雜度 O(N)
function test3(data){
    // 不先將陣列排序， 直接找兩個最大及兩個最小
    // init max and secondmax
    let max = data[0];
    let secondMax = data[1];
    if (secondMax > max){
        [max, secondMax] = [secondMax, max];
    }
    // init min and secondMin
    let min = data[0];
    let secondMin = data[1];
    if (secondMin < min){
        [min, secondMin] = [secondMin, min];
    }
    //find
    for (let i=0; i<data.length;i++){
        if (data[i]>max){
            secondMax =max;
            max = data[i];
        } else if (data[i]>secondMax){
            secondMax = data[i];
        }
        if (data[i]<min){
            secondMin = min;
            min = data[i];
        } else if (data[i]<secondMin){
            secondMin = data[i];
        }
    }
    let ans = max*secondMax;
    if (min*secondMin>ans){
        ans = min*secondMin;
    }
    console.log(ans)
}
// 將資料的宣告統一放在最下面，但在執行呼叫之前
// let data = [3, -5, -2, 8, 6,-10];

// test1(data);
// test2(data);
// test3(data);

// 如果要處理的資料量小，那根本沒在乎效率問題
// 評估程式效率，須想辦法排除硬體、電腦運作現況等等非程式造成的外部因素
// 時間複雜度 time complexity:程式的執行時間，和輸入資料量的關係


// 假設輸入的資料量從 1 萬，變成 100 萬，放大 100 倍。
// 那麼，程式要執行的時間放大幾倍呢？
// 如果 A 程式執行時間不變動：常數時間複雜度，又稱為 O(1)
// 如果 A 程式執行時間放大 7 倍：Log 時間複雜度，又稱為 O(log(N))， N 代表資料的數量
// 如果 A 程式執行時間也放大 100 倍：線性時間複雜度，又稱為 O(N)， N 代表資料的數量
// 如果 A 程式執行時間放大 10000 倍：平方時間複雜度，又稱為 O(N^2)， N 代表資料的數量

// 測試資料
let dataSize = 100000

let data =[];
for (let i =0;i< dataSize;i++){
    data.push(parseInt(Math.random()*10000 -5000)); 
    //乘以 10000 之後，數值區間被拉長了，減去 5000 後，整個數值區間往負數方向「平移」了 5000
}

// console.log("兩兩相乘");
// console.time();
// test1(data);
// console.timeEnd()

// console.log("排序");
// console.time();
// test2(data);
// console.timeEnd()

console.log("直接找");
console.time();
test3(data);
console.timeEnd()

// 測試成果
// 1000：3、1.6 、0.6
// 10000：97、1.9、1
// 100000：8250、24、1.4