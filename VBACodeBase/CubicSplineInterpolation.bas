Attribute VB_Name = "CubicSplineInterpolation"
Option Explicit

Public Function GetCubicSplineMatrix(x As Range) As Double()
    Dim i, cnt As Integer
    
    cnt = x.Cells.Count - 1
    
    Dim tempX() As Double
    
    ReDim tempX(0 To cnt)

    Dim variantX As Variant
    
    variantX = x.Value

    If IsArray(variantX) Then
        For i = 1 To cnt + 1
            tempX(i - 1) = variantX(i, 1)
        Next
    End If
       
    'If (IsArray(tempX) And IsArray(tempY)) Then
        Dim matrix() As Double
        ReDim matrix(1 To 4 * cnt, 1 To 4 * cnt)
    
        matrix(1, 3) = 2
        matrix(1, 4) = 6 * tempX(0)
        
        matrix(4 * cnt, 4 * cnt - 1) = 2
        matrix(4 * cnt, 4 * cnt) = 6 * tempX(cnt)
        
        For i = 1 To cnt
            matrix(4 * i - 2, 4 * i - 3) = 1
            matrix(4 * i - 2, 4 * i - 2) = tempX(i - 1)
            
            matrix(4 * i - 2, 4 * i - 1) = tempX(i - 1) ^ 2
            matrix(4 * i - 2, 4 * i) = tempX(i - 1) ^ 3
            
            matrix(4 * i - 1, 4 * i - 3) = 1
            matrix(4 * i - 1, 4 * i - 2) = tempX(i)
            
            matrix(4 * i - 1, 4 * i - 1) = tempX(i) ^ 2
            matrix(4 * i - 1, 4 * i) = tempX(i) ^ 3
            
            If i < cnt Then
                matrix(4 * i, 4 * i - 2) = 1
                matrix(4 * i, 4 * i - 1) = 2 * tempX(i)
                
                matrix(4 * i, 4 * i) = 3 * (tempX(i) ^ 2)
                matrix(4 * i, 4 * i + 2) = -1
                
                matrix(4 * i, 4 * i + 3) = -2 * tempX(i)
                matrix(4 * i, 4 * i + 4) = -3 * (tempX(i) ^ 2)
                
                matrix(4 * i + 1, 4 * i - 1) = 2
                matrix(4 * i + 1, 4 * i) = 6 * tempX(i)
                
                matrix(4 * i + 1, 4 * i + 3) = -2
                matrix(4 * i + 1, 4 * i + 4) = -6 * tempX(i)
            End If
        Next
    'End If
    
    GetCubicSplineMatrix = matrix
End Function

Public Function GetCubicSplineMatrixVariant(variantX As Variant) As Double()
    Dim i, cnt As Integer
    
    'cnt = x.Cells.Count - 1
    cnt = UBound(variantX) - 1

    Dim tempX() As Double
    
    ReDim tempX(0 To cnt)

    If IsArray(variantX) Then
        For i = 1 To cnt + 1
            tempX(i - 1) = variantX(i, 1)
        Next
    End If
       
    'If (IsArray(tempX) And IsArray(tempY)) Then
        Dim matrix() As Double
        ReDim matrix(1 To 4 * cnt, 1 To 4 * cnt)
    
        matrix(1, 3) = 2
        matrix(1, 4) = 6 * tempX(0)
        
        matrix(4 * cnt, 4 * cnt - 1) = 2
        matrix(4 * cnt, 4 * cnt) = 6 * tempX(cnt)
        
        For i = 1 To cnt
            matrix(4 * i - 2, 4 * i - 3) = 1
            matrix(4 * i - 2, 4 * i - 2) = tempX(i - 1)
            
            matrix(4 * i - 2, 4 * i - 1) = tempX(i - 1) ^ 2
            matrix(4 * i - 2, 4 * i) = tempX(i - 1) ^ 3
            
            matrix(4 * i - 1, 4 * i - 3) = 1
            matrix(4 * i - 1, 4 * i - 2) = tempX(i)
            
            matrix(4 * i - 1, 4 * i - 1) = tempX(i) ^ 2
            matrix(4 * i - 1, 4 * i) = tempX(i) ^ 3
            
            If i < cnt Then
                matrix(4 * i, 4 * i - 2) = 1
                matrix(4 * i, 4 * i - 1) = 2 * tempX(i)
                
                matrix(4 * i, 4 * i) = 3 * (tempX(i) ^ 2)
                matrix(4 * i, 4 * i + 2) = -1
                
                matrix(4 * i, 4 * i + 3) = -2 * tempX(i)
                matrix(4 * i, 4 * i + 4) = -3 * (tempX(i) ^ 2)
                
                matrix(4 * i + 1, 4 * i - 1) = 2
                matrix(4 * i + 1, 4 * i) = 6 * tempX(i)
                
                matrix(4 * i + 1, 4 * i + 3) = -2
                matrix(4 * i + 1, 4 * i + 4) = -6 * tempX(i)
            End If
        Next
    'End If
    
    GetCubicSplineMatrixVariant = matrix
End Function

Public Function GetCubicSplineVector(y As Range) As Double()
    Dim variantY As Variant
    
    variantY = y.Value

    Dim i, cnt As Integer
    
    cnt = y.Cells.Count - 1

    If IsArray(variantY) Then
        Dim vector() As Double
        ReDim vector(1 To cnt * 4, 1 To 1)
        
        vector(1, 1) = 0
        vector(cnt * 4, 1) = 0
        
        For i = 1 To cnt
            vector(4 * i - 2, 1) = variantY(i, 1)
            
            vector(4 * i - 1, 1) = variantY(i + 1, 1)
            
            If i < cnt Then
                vector(4 * i, 1) = 0
                
                vector(4 * i + 1, 1) = 0
            End If
        Next
    End If
    
    GetCubicSplineVector = vector
End Function

Public Function GetCubicSplineVectorVariant(variantY As Variant) As Double()
    Dim i, cnt As Integer
    
    cnt = UBound(variantY) - 1

    If IsArray(variantY) Then
        Dim vector() As Double
        ReDim vector(1 To cnt * 4, 1 To 1)
        
        vector(1, 1) = 0
        vector(cnt * 4, 1) = 0
        
        For i = 1 To cnt
            vector(4 * i - 2, 1) = variantY(i, 1)
            
            vector(4 * i - 1, 1) = variantY(i + 1, 1)
            
            If i < cnt Then
                vector(4 * i, 1) = 0
                
                vector(4 * i + 1, 1) = 0
            End If
        Next
    End If
    
    GetCubicSplineVectorVariant = vector
End Function


Function PowerMatrix(rngInp As Range, lngPow As Long) As Variant
Dim i As Long
PowerMatrix = rngInp
If lngPow > 1 Then
  For i = 2 To lngPow
    PowerMatrix = Application.WorksheetFunction.MMult(rngInp, PowerMatrix)
  Next
End If
End Function

Public Function GetCubicSplineParameters(x As Range, y As Range) As Variant
    Dim matrix() As Double
    Dim vector() As Double
    
    matrix = GetCubicSplineMatrix(x)
    
    vector = GetCubicSplineVector(y)
    
    GetCubicSplineParameters = Application.WorksheetFunction.MMult(Application.WorksheetFunction.MInverse(matrix), vector)
End Function


Public Function GetCubicSplineParametersTranspose(x As Range, y As Range) As Variant
    Dim x_Transpose As Variant
    Dim y_transpose As Variant
    
    x_Transpose = Application.WorksheetFunction.Transpose(x.Value)
    
    y_transpose = Application.WorksheetFunction.Transpose(y.Value)
    
    'GetCubicSplineParametersTranspose = Application.WorksheetFunction.Transpose(GetCubicSplineParameters(x_Transpose, y_transpose))
    
    Dim matrix() As Double
    Dim vector() As Double
    
    matrix = GetCubicSplineMatrixVariant(x_Transpose)
    
    vector = GetCubicSplineVectorVariant(y_transpose)
    
    GetCubicSplineParametersTranspose = Application.WorksheetFunction.MMult(Application.WorksheetFunction.MInverse(matrix), vector)
    'GetCubicSplineParametersTranspose = Application.WorksheetFunction.MMult(Application.WorksheetFunction.MInverse(Matrix), Vector)
    
    GetCubicSplineParametersTranspose = Application.WorksheetFunction.Transpose(GetCubicSplineParametersTranspose)
End Function



Public Function SolveODENumeric(a As Double, b As Double, interval As Integer) As Variant
    Dim n As Integer
    n = 2 ^ interval

    Dim h As Double
    h = (b - a) / n
    
    Dim matrix() As Double
    ReDim matrix(1 To n - 1, 1 To n - 1)
    
    Dim vector() As Double
    ReDim vector(1 To n - 1, 1 To 1)
    
    Dim y_0_co As Double
    y_0_co = 1 - h
    
    Dim y_i_co As Double
    y_i_co = h ^ 2 - 2
    
    Dim y_i2_co As Double
    y_i2_co = 1 + h
    
    Dim i As Integer
    For i = 3 To n - 1
    
        matrix(i, i - 2) = y_0_co
        matrix(i, i - 1) = y_i_co
        matrix(i, i) = y_i2_co
    
        vector(i, 1) = 0
    Next
    
    Dim y0 As Double
    y0 = 2
    
    Dim y1 As Double
    y1 = y0 - h
    
    'Initial condition of f(a)
    matrix(1, 1) = y_i2_co

    vector(1, 1) = -1 * y0 * y_0_co - y_i_co * y1
    
    matrix(2, 1) = y_i_co
    matrix(2, 2) = y_i2_co
    vector(2, 1) = -1 * y1 * y_0_co
    
    Dim temp As Variant
    
    temp = Application.WorksheetFunction.MMult(Application.WorksheetFunction.MInverse(matrix), vector)
    
    Dim result() As Double
    ReDim result(1 To n, 1 To 1)
    
    result(1, 1) = y1
    
    For i = 1 To n - 1
        result(1 + i, 1) = temp(i, 1)
    Next
    
    SolveODENumeric = result
End Function


Public Function GetEfficientCubicSplineMatrix(x As Range) As Double()
    Dim variantX As Variant
    variantX = x.Value
    
    GetEfficientCubicSplineMatrix = GetEfficientCubicSplineMatrixVariant(variantX)
End Function


Public Function GetEfficientCubicSplineMatrixVariant(variantX As Variant) As Double()

    Dim cnt As Integer
    cnt = UBound(variantX) - 2
    
    Dim matrix() As Double
    ReDim matrix(1 To cnt, 1 To cnt)
        
    Dim tempX() As Double
    ReDim tempX(0 To cnt + 1)

    Dim i As Integer

    For i = 1 To UBound(variantX)
        tempX(i - 1) = variantX(i, 1)
    Next
    
    For i = 1 To cnt
        matrix(i, i) = 2 * (tempX(i + 1) - tempX(i - 1))
        
        If i < cnt Then
            matrix(i, i + 1) = tempX(i + 1) - tempX(i)
        End If
        
        If i > 1 Then
            matrix(i, i - 1) = tempX(i) - tempX(i - 1)
        End If
    Next
    
    GetEfficientCubicSplineMatrixVariant = matrix
End Function

Public Function GetEfficientCubicSplineVector(x As Range, y As Range) As Double()
    Dim variantY As Variant
    variantY = y.Value
    
    Dim variantX As Variant
    variantX = x.Value
    
    Dim resultVector() As Double
    resultVector = GetEfficientCubicSplineVectorVariant(variantX, variantY)
    
    GetEfficientCubicSplineVector = resultVector
End Function

Public Function GetEfficientCubicSplineVectorVariant(variantX As Variant, variantY As Variant) As Double()
    Dim i, cnt As Integer
    
    cnt = UBound(variantY) - 2

    Dim vector() As Double
    ReDim vector(1 To cnt, 1 To 1)
        
    Dim tempX() As Double
    ReDim tempX(0 To cnt + 1)

    For i = 1 To UBound(variantX)
        tempX(i - 1) = variantX(i, 1)
    Next
    
    Dim tempY() As Double
    ReDim tempY(0 To cnt + 1)
    
    For i = 1 To UBound(variantY)
        tempY(i - 1) = variantY(i, 1)
    Next
    
    For i = 1 To cnt
        vector(i, 1) = 6 * ((tempY(i + 1) - tempY(i)) / (tempX(i + 1) - tempX(i)) - (tempY(i) - tempY(i - 1)) / (tempX(i) - tempX(i - 1)))
    Next
    
    GetEfficientCubicSplineVectorVariant = vector
End Function


Public Function GetEfficientCubicSplineParameters(x As Range, y As Range)
    Dim variantY As Variant
    variantY = y.Value
    
    Dim variantX As Variant
    variantX = x.Value
    
    GetEfficientCubicSplineParameters = GetEfficientCubicSplineParametersVariant(variantX, variantY)
End Function


Public Function GetEfficientCubicSplineParametersVariant(variantX As Variant, variantY As Variant) As Variant
    Dim matrix() As Double
    matrix = GetEfficientCubicSplineMatrixVariant(variantX)
    
    Dim vector As Variant
    vector = GetEfficientCubicSplineVectorVariant(variantX, variantY)
    
    Dim variantW As Variant
    variantW = Application.WorksheetFunction.MMult(Application.WorksheetFunction.MInverse(matrix), vector)
    
    Dim cnt As Integer
    cnt = UBound(variantX)
    
    Dim vectorW() As Double
    ReDim vectorW(1 To cnt, 1 To 1)
    
    vectorW(1, 1) = 0
    vectorW(cnt, 1) = 0
    
    Dim i As Integer
    For i = 2 To cnt - 1
        vectorW(i, 1) = variantW(i - 1, 1)
    Next
    
    Dim tempResult() As Double
    ReDim tempResult(1 To cnt - 1, 1 To 2)
    For i = 1 To cnt - 1
        'double c = (inputWs[i - 1] * inputXs[i] - inputWs[i] * inputXs[i - 1]) / (2.0 * (inputXs[i] - inputXs[i - 1]));

        'double d = (inputWs[i] - inputWs[i - 1]) / (6.0 * (inputXs[i] - inputXs[i - 1]));
    
        tempResult(i, 1) = (vectorW(i, 1) * variantX(i + 1, 1) - vectorW(i + 1, 1) * variantX(i, 1)) / (2 * (variantX(i + 1, 1) - variantX(i, 1)))
        
        tempResult(i, 2) = (vectorW(i + 1, 1) - vectorW(i, 1)) / (6 * (variantX(i + 1, 1) - variantX(i, 1)))
    Next
    
    Dim tempResult2() As Double
    ReDim tempResult2(1 To cnt - 1, 1 To 2)
    
    For i = 1 To cnt - 1
        'double q = inputYs[i - 1] - tempResult[i - 1].Item1 * Math.Pow(inputXs[i - 1], 2) - tempResult[i - 1].Item2 * Math.Pow(inputXs[i - 1], 3);

        'double r = inputYs[i] - tempResult[i - 1].Item1 * Math.Pow(inputXs[i], 2) - tempResult[i - 1].Item2 * Math.Pow(inputXs[i], 3);
        
        tempResult2(i, 1) = variantY(i, 1) - tempResult(i, 1) * variantX(i, 1) ^ 2 - tempResult(i, 2) * variantX(i, 1) ^ 3
        
        tempResult2(i, 2) = variantY(i + 1, 1) - tempResult(i, 1) * variantX(i + 1, 1) ^ 2 - tempResult(i, 2) * variantX(i + 1, 1) ^ 3
    Next
    
    Dim finalResult() As Double
    ReDim finalResult(1 To cnt - 1, 1 To 4)
    
    For i = 1 To cnt - 1
        'double a = (tempResult2[i - 1].Item1 * inputXs[i] - tempResult2[i- 1].Item2 * inputXs[i - 1]) / (inputXs[i] - inputXs[i - 1]);

        'double b = (tempResult2[i - 1].Item2 - tempResult2[i - 1].Item1) / (inputXs[i] - inputXs[i - 1]);
        
        finalResult(i, 1) = (tempResult2(i, 1) * variantX(i + 1, 1) - tempResult2(i, 2) * variantX(i, 1)) / (variantX(i + 1, 1) - variantX(i, 1))
        
        finalResult(i, 2) = (tempResult2(i, 2) - tempResult2(i, 1)) / (variantX(i + 1, 1) - variantX(i, 1))
        
        finalResult(i, 3) = tempResult(i, 1)
        
        finalResult(i, 4) = tempResult(i, 2)
    Next
    
    GetEfficientCubicSplineParametersVariant = finalResult
End Function


Public Function GetZeroRateFromEfficientCubicSpline(x As Range, y As Range, t As Range) As Variant
    Dim cubicSplineParams As Variant
    cubicSplineParams = GetEfficientCubicSplineParameters(x, y)
    
    Dim variantT As Variant
    variantT = t.Value
    
    Dim variantX As Variant
    variantX = x.Value
    
    Dim zeroRates() As Double
    ReDim zeroRates(1 To UBound(variantT), 1 To 1)
    
    Dim i As Integer
    Dim j As Integer
    For i = 1 To UBound(variantT)
        For j = 1 To UBound(cubicSplineParams, 1)
            If variantT(i, 1) < variantX(i + 1, 1) Then
                zeroRates(i, 1) = cubicSplineParams(i, 1) + cubicSplineParams(i, 2) * variantT(i, 1) + cubicSplineParams(i, 3) * variantT(i, 1) ^ 2 _
                + cubicSplineParams(i, 4) * variantT(i, 1) ^ 3
                
                GoTo ContinueLoop
            ElseIf variantT(i, 1) < variantX(i + 2, 1) Then
                zeroRates(i, 1) = cubicSplineParams(i + 1, 1) + cubicSplineParams(i + 1, 2) * variantT(i, 1) + cubicSplineParams(i + 1, 3) * variantT(i, 1) ^ 2 _
                + cubicSplineParams(i + 1, 4) * variantT(i, 1) ^ 3
                
                GoTo ContinueLoop
            ElseIf variantT(i, 1) < variantX(i + 3, 1) Then
                zeroRates(i, 1) = cubicSplineParams(i + 2, 1) + cubicSplineParams(i + 2, 2) * variantT(i, 1) + cubicSplineParams(i + 2, 3) * variantT(i, 1) ^ 2 _
                + cubicSplineParams(i + 2, 4) * variantT(i, 1) ^ 3
                
                GoTo ContinueLoop
            Else
                zeroRates(i, 1) = cubicSplineParams(i + 3, 1) + cubicSplineParams(i + 3, 2) * variantT(i, 1) + cubicSplineParams(i + 3, 3) * variantT(i, 1) ^ 2 _
                + cubicSplineParams(i + 3, 4) * variantT(i, 1) ^ 3
            End If
        Next
        
ContinueLoop:
    Next
    
    GetZeroRateFromEfficientCubicSpline = zeroRates
End Function
