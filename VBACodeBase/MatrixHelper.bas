Attribute VB_Name = "MatrixHelper"
Option Explicit

Public Function Magnitude(v As Variant) As Variant
    Dim i As Integer
    Dim t As Double
    
    On Error GoTo ErrH
    
    Select Case TypeName(v)
        Case "Range"
            Dim c As Range
            
            For Each c In v
                t = t + c.Value ^ 2
            Next c
            Set c = Nothing
        Case "Variant()", "Integer()", "Double()"
            For i = 0 To UBound(v) - LBound(v)
                t = t + v(i + LBound(v)) ^ 2
            Next i
        Case Else
            ' TODO: Handle other types
            Magnitude = "Magnitude not valid"
            Exit Function
    End Select
    Magnitude = t ^ 0.5
Ex:
    Exit Function
ErrH:
    Debug.Assert (MsgBox(Error$ & vbCrLf & "Do you want to debug?", vbYesNo) = vbNo)
    
    Resume Ex
    
End Function


Public Function Dot(vectorA As Variant, vectorB As Variant) As Variant
    Dim a(), b() As Double
    Dim i As Integer
    Dim r As Double
    Dim c As Range

    On Error GoTo ErrH
    
    Select Case TypeName(vectorA)
        Case "Range"
            If vectorA.Count > 1 Then
                ReDim a(vectorA.Count - 1)
                
                i = 0
                For Each c In vectorA
                    a(i) = CDbl(c.Value)
                    i = i + 1
                Next c
            Else
                ' TODO: Handle other entries
                Dot = "Dot product not valid"
                Exit Function
            End If
        Case "Variant()", "Integer()", "Double()"
            If UBound(vectorA) - LBound(vectorA) > 0 Then
                ReDim a(UBound(vectorA) - LBound(vectorA))
                
                For i = 0 To UBound(a)
                    a(i) = CDbl(vectorA(i + LBound(vectorA)))
                Next i
            Else
                ' TODO: Handle other entries
                Dot = "Dot product not valid"
                Exit Function
            End If
        Case Else
            ' TODO: Handle other types
            Dot = "Dot product not valid"
            Exit Function
    End Select
    Select Case TypeName(vectorB)
        Case "Range"
            If vectorB.Count = vectorA.Count Then
                ReDim b(vectorB.Count - 1)
                
                i = 0
                For Each c In vectorB
                    b(i) = CDbl(c.Value)
                    i = i + 1
                Next c
            Else
                ' TODO: Handle other entries
                Dot = "Dot product not valid"
                Exit Function
            End If
        Case "Variant()", "Integer()", "Double()"
            If UBound(vectorB) - LBound(vectorB) = UBound(a) Then
                ReDim b(UBound(a))
                
                For i = 0 To UBound(b)
                    b(i) = CDbl(vectorB(i + LBound(vectorB)))
                Next i
            Else
                ' TODO: Handle other entries
                Dot = "Dot product not valid"
                Exit Function
            End If
        Case Else
            ' TODO: Handle other types
            Dot = "Dot product not valid"
            Exit Function
    End Select
    
    For i = 0 To UBound(a)
        r = r + a(i) * b(i)
    Next i
    Dot = r
Ex:
    Set c = Nothing
    Exit Function
ErrH:
    Debug.Assert (MsgBox(Error$ & vbCrLf & "Do you want to debug?", vbYesNo) = vbNo)

    Resume Ex
    Resume

End Function


Public Function GetUnitVector(v As Variant) As Variant
    Dim m, a() As Double
    Dim i As Integer
    Dim r() As Variant
    Dim c As Range
    
    On Error GoTo ErrH
    
    Select Case TypeName(v)
        Case "Range"
            ReDim a(v.Count - 1)
            ReDim r(v.Count - 1)
            
            i = 0
            For Each c In v
                a(i) = CDbl(c.Value)
                i = i + 1
            Next c
        Case "Variant()", "Integer()", "Double()"
            ReDim a(UBound(v) - LBound(v))
            ReDim r(UBound(a))
            
            For i = 0 To UBound(a)
                a(i) = CDbl(v(i + LBound(v)))
            Next i
        Case Else
            ' TODO: Handle other types
            GetUnitVector = "Input vector not valid"
            Exit Function
    End Select
    
    m = Magnitude(a)
    If m = 0 Then
        For i = 0 To UBound(r)
            r(i) = "Inf"
        Next i
        Exit Function
    Else
        For i = 0 To UBound(r)
            r(i) = a(i) / m
        Next i
    End If

    If TypeName(Application.Caller) = "Range" Then
        If Application.Caller.Rows.Count > 1 Then
            GetUnitVector = Application.WorksheetFunction.Transpose(r)
        Else
            GetUnitVector = r
        End If
    Else
        GetUnitVector = r
    End If
Ex:
    Set c = Nothing
    Exit Function
ErrH:
    Debug.Assert (MsgBox(Error$ & vbCrLf & "Do you want to debug?", vbYesNo) = vbNo)
    Resume Ex
    Resume
End Function
