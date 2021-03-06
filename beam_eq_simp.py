# -*- coding: utf-8 -*-
""" Sam Parry u1008557 04/06/21"""
from sympy import *
def simplify_beam_eq(equation):
    """
    Simplifies the equation returned by the BINGO beam_bending problem.
    :param equation: Unsimplifies expression as a String
    :return: Expanded and Simplified polynomial
    """
    eq = equation.replace('X_0', 'x').replace(')(', '*')
    x = symbols('x')
    smpl = str(simplify(eq).expand())   # simplifies and expands the eq.
    smpl = str(smpl).replace('*I', '')  # converts eq back to a string and removes any potential imaginary numbers
    return smpl


def main():
    # 3 unsimplified sample equations
    eq = [
        '(X_0 + -10.000000148238323 - (((X_0)((X_0 + -10.000000148238323)/(-10.000000148238323) ))((X_0 + '
        '-10.000000148238323)/(-10.000000148238323) )))((X_0)/(-4799.999951370799) )',

        '(((-986.4820369723794)/(5.000000223163965 + 5.000000223163965)  + (X_0)(X_0 - (5.000000223163965 + '
        '5.000000223163965)))/(474535.8931856667) )((X_0)(X_0 - (5.000000223163965 + 5.000000223163965)))',

        '(((((X_0)((-2.0737034047292067)/(-2.0737034047292067) ))/((-1480.7306455862074)/((-2.0737034047292067)/('
        '-2.0737034047292067) ) ) )(-2.0737034047292067))((-1480.7306455862074 - ((-2.0737034047292067)('
        '-2.0737034047292067)))^((-2.0737034047292067)^(-2.0737034047292067)) - ((X_0)((-2.0737034047292067)/('
        '-2.0737034047292067) ) - ((-1480.7306455862074 - ((-2.0737034047292067)(-2.0737034047292067)))^(('
        '-2.0737034047292067)^(-2.0737034047292067))))) + 0.15039612381462963)(((((X_0)((-2.0737034047292067)/('
        '-2.0737034047292067) ))/((-1480.7306455862074)/((-2.0737034047292067)/(-2.0737034047292067) ) ) )('
        '-2.0737034047292067))((-1480.7306455862074 - ((-2.0737034047292067)(-2.0737034047292067)))^(('
        '-2.0737034047292067)^(-2.0737034047292067)) - ((X_0)((-2.0737034047292067)/(-2.0737034047292067) ) - (('
        '-1480.7306455862074 - ((-2.0737034047292067)(-2.0737034047292067)))^((-2.0737034047292067)^('
        '-2.0737034047292067))))))']
    print(simplify_beam_eq(eq[0]))
main()
