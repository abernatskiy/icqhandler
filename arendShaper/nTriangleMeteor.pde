import java.util.Map;

ArrayList<float[]> points = new ArrayList<float[]>();
ArrayList<int[]> triangles = new ArrayList<int[]>();
float[] weights;
float[] tone;
float[][] distMatrix;
float PHI=(1.0 + sqrt(5.0)) / 2.0;
float r=1.0;
float a=(1.0/2.0)*r;
float b=(1.0/(2.0*PHI))*r;
float baseScale=10.0;



void setup() {
    size(642, 642, P3D);

    Table pointTable= loadTable("points.csv", "header");
    for (int i=0; i<pointTable.getRowCount(); i++) {
        float[] point=new float[3];
        String[] colLabel={"X", "Y", "Z"};
        for (int j=0; j<3; j++) {
            String S=pointTable.getString(i, colLabel[j]);
            switch(S) {
            case "a":
                point[j]=a; 
                break;
            case "b":
                point[j]=b; 
                break;
            case "-a":
                point[j]=-a; 
                break;
            case "-b":
                point[j]=-b; 
                break;
            case "0":
                point[j]=0.0; 
                break;
            }
        }
        points.add(point);
        float l = sqrt( (points.get(i)[0] * points.get(i)[0]) + 
            (points.get(i)[1] * points.get(i)[1]) + 
            (points.get(i)[2] * points.get(i)[2]));
        for (int j=0; j<3; j++)
            points.get(i)[j]/=l;
    }
    Table triangleTable= loadTable("faces.csv", "header");
    for (int i=0; i<triangleTable.getRowCount(); i++) {
        int[] triangle=new int[3];
        triangle[0]=triangleTable.getInt(i, "p1");
        triangle[1]=triangleTable.getInt(i, "p2");
        triangle[2]=triangleTable.getInt(i, "p3");
        triangles.add(triangle);
    }
    
    //increase the reps number to get a finer resolution
    for (int reps=0; reps<2; reps++) {
        ArrayList<int[]> newTs = new ArrayList<int[]>();
        ArrayList<float[]> newPs = new ArrayList<float[]>();
        for (int n=0; n<triangles.size(); n++) {
            float[][] P=new float[3][3];
            float[][] NP=new float[3][3];

            //find original points
            for (int i=0; i<3; i++)
                for (int j=0; j<3; j++) {
                    NP[i][j]=0.0;
                    P[i][j]=points.get(triangles.get(n)[i])[j];
                }
            //compute new midpoints
            for (int i=0; i<3; i++) {
                for (int j=0; j<3; j++) {
                    NP[i][j]=(P[i][j]+P[(i+1)%3][j])/2.0;
                }
            }
            //renormalize midpoints
            for (int i=0; i<3; i++) {
                float l=sqrt((NP[i][0]*NP[i][0])+
                    (NP[i][1]*NP[i][1])+
                    (NP[i][2]*NP[i][2]));
                for (int j=0; j<3; j++)
                    NP[i][j]/=l;
            }
            int baseN=newPs.size();
            newPs.add(P[0]);
            newPs.add(P[1]);
            newPs.add(P[2]);
            newPs.add(NP[0]);
            newPs.add(NP[1]);
            newPs.add(NP[2]);
            int[] T0=new int[3];
            int[] T1=new int[3];
            int[] T2=new int[3];
            int[] T3=new int[3];
            T0[0]=baseN; 
            T0[1]=baseN+3; 
            T0[2]=baseN+5;
            T1[0]=baseN+3; 
            T1[1]=baseN+1; 
            T1[2]=baseN+4;
            T2[0]=baseN+4; 
            T2[1]=baseN+2; 
            T2[2]=baseN+5;
            T3[0]=baseN+3; 
            T3[1]=baseN+4; 
            T3[2]=baseN+5;
            newTs.add(T0);
            newTs.add(T1);
            newTs.add(T2);
            newTs.add(T3);
        }
        IntDict I=new IntDict();
        int indexC=0;
        for (int i=0; i<newPs.size(); i++) {
            String S=newPs.get(i)[0]+","+newPs.get(i)[1]+","+newPs.get(i)[2];
            //println(S);
            if (!I.hasKey(S)) {
                I.set(S, indexC);
                indexC++;
            }
        }
        triangles.clear();
        //println(I.keyArray());
        for (int i=0; i<newTs.size(); i++) {
            int[] corners=newTs.get(i);
            int[] newCorners=new int[3];
            for (int j=0; j<3; j++) {
                String S=newPs.get(corners[j])[0]+","+newPs.get(corners[j])[1]+","+newPs.get(corners[j])[2];
                newCorners[j]=I.get(S);
            }
            triangles.add(newCorners);
        }
        I.sortValues();
        points.clear();
        String[] KA=I.keyArray();
        for (int i=0; i<KA.length; i++) {
            String[] S=KA[i].split(",");
            float[] P=new float[3];
            for (int j=0; j<3; j++)
                P[j]=float(S[j]);
            points.add(P);
        }
        println("HM:", I.size());
        //points=newPs;
        //triangles=newTs;
    }
    weights=new float[points.size()];
    for (int i=0; i<points.size(); i++) {
        weights[i]=0.3;//random(0.2, 0.5);
    }
    tone=new float[triangles.size()];
    for (int i=0; i<triangles.size(); i++)
        tone[i]=random(160, 180);

    println("triangles:", triangles.size());
    println("points:", points.size());
    println("weights:", weights.length);
    //compute distMatrix
    distMatrix=new float[points.size()][points.size()];
    for (int i=0; i<points.size(); i++) {
        for (int j=0; j<points.size(); j++) {
            if (i==j) {
                distMatrix[i][j]=0.0;
            } else {
                float[] A=points.get(i);
                float[] B=points.get(j);
                float[] deltas=new float[3];
                for (int k=0; k<3; k++)
                    deltas[k]=A[k]-B[k];
                float l=sqrt((deltas[0]*deltas[0])+
                    (deltas[1]*deltas[1])+
                    (deltas[2]*deltas[2]));
                distMatrix[i][j]=l;
            }
        }
    }

    //println(distMatrix[0]);
    //add Bump
    for (int b=0; b<200; b++) {
        int bumpID=(int) random(weights.length);
        float bumpWeight=random(-0.1, 0.1)*((float)b/200.0);
        float bumpRadius=random(0.4, 1.0);
        for (int i=0; i<weights.length; i++)
            if (distMatrix[bumpID][i]<bumpRadius)
                weights[i]+=bumpWeight*(bumpRadius-distMatrix[bumpID][i]);
    }
}

float rx=0.0;
float ry=0.0;
float rz=0.0;

void draw() {
    background(0);
    lights();
    //    directionalLight(126, 126, 126, 0, 0, -1);
    noStroke();
    fill(color(178, 178, 178));
    translate(width/2, height/2, 0);
    rotateX(rx);
    rotateY(ry);
    rotateZ(rz);
    rx+=0.01;
    ry+=0.001;
    rz+=0.03;
    /*
    switch(state){
     case 0: rotateX(0.0);
     rotateY(0.0);
     rotateZ(0.0); break;
     case 1: rotateX(120.0);
     rotateY(0.0);
     rotateZ(0.0); break;
     case 2: rotateX(120.0);
     rotateY(120.0);
     rotateZ(0.0); break;
     case 3: rotateX(120.0);
     rotateY(240.0);
     rotateZ(0.0); break;
     }
     */
    //println(triangles.size());
    //println(points.size());
    beginShape(TRIANGLES);
    for (int i=0; i<triangles.size(); i++) {
        if(i==0)
            fill(color(256,100,100));
        else
            fill(color(tone[i], tone[i], tone[i]));
        for (int j=0; j<3; j++) {
            float weight=weights[triangles.get(i)[j]];
            vertex( points.get(triangles.get(i)[j])[0]*50.0*weight*baseScale, 
                points.get(triangles.get(i)[j])[1]*50.0*weight*baseScale, 
                points.get(triangles.get(i)[j])[2]*50.0*weight*baseScale);
        }
    }
    endShape();
}
